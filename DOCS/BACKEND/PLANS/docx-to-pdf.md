# Implementation Plan: DOCX to PDF Conversion

**Date**: 2026-07-14
**Spec**: `DOCS/BACKEND/SPECS/docx-to-pdf.md`

## Summary

Accept Office documents (DOCX, XLSX, PPTX) and convert them to PDF using LibreOffice headless. Detect LibreOffice at startup via platform-specific paths. Preserve text, formatting, tables, images, lists, headers, and footers.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: LibreOffice (system-installed, headless mode via `subprocess`)
**Storage**: tempfile + pathlib (local filesystem)
**Testing**: pytest with mocked `subprocess` calls
**Target Platform**: Windows, macOS, Linux (cross-platform desktop via Electron)
**Project Type**: Single backend service with hexagonal architecture
**Performance Goals**: 20-page DOCX → PDF in <15 seconds
**Constraints**: Requires LibreOffice installed on host system. Missing fonts will be substituted. 3-minute timeout for large documents.
**Scale/Scope**: Single-user desktop app.

## Project Structure

### Documentation (this feature)

```
DOCS/BACKEND/
├── SPECS/docx-to-pdf.md
└── PLANS/docx-to-pdf.md   # This file
```

### Source Code (repository root)

```
backend/
├── adapters/
│   └── output/
│       └── converters/
│           └── office_to_pdf_adapter.py   # THIS FEATURE
├── infrastructure/
│   └── main.py                            # Wiring: register adapter
└── tests/
    ├── unit/
    │   └── test_office_to_pdf_adapter.py
    └── integration/
        └── test_office_to_pdf_e2e.py
```

**Structure Decision**: This plan assumes the hexagonal skeleton already exists. Only the adapter file and its registration are added. The adapter handles all Office formats (DOCX, XLSX, PPTX) since they all use LibreOffice headless — a single adapter with multiple `supports()` entries rather than three separate adapters.

## Phase 1: Setup

**Purpose**: Create the adapter file.

- [ ] T001 Create `backend/adapters/output/converters/office_to_pdf_adapter.py` skeleton implementing `FileConverterPort` (empty `supports()` and `convert()` methods)
- [ ] T002 Register `OfficeToPdfAdapter` in `backend/infrastructure/main.py` wiring
- [ ] T003 Add `FileFormat.DOCX`, `FileFormat.XLSX`, `FileFormat.PPTX` entries to `domain/entities.py` if not already present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: LibreOffice discovery and smoke testing.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Implement LibreOffice path detection per platform:
  - Windows: `C:\Program Files\LibreOffice\program\soffice.exe`
  - macOS: `/Applications/LibreOffice.app/Contents/MacOS/soffice`
  - Linux: `shutil.which("libreoffice")` or `shutil.which("soffice")`
- [ ] T005 Implement startup check in `main.py`: on app boot, verify LibreOffice binary exists and is executable. If not, log a warning with install instructions (but don't crash — the adapter will raise `ConversionError` at conversion time).
- [ ] T006 Create `tests/unit/test_office_to_pdf_adapter.py` with smoke test: instantiate adapter, verify `supports()` returns correct values for DOCX→PDF, XLSX→PDF, PPTX→PDF, and `False` for non-Office formats
- [ ] T007 Mock `subprocess.run` in tests to avoid requiring LibreOffice during unit testing

**Checkpoint**: Adapter registered, LibreOffice detection functional, tests run with mocks.

---

## Phase 3: User Story 1 - Basic DOCX to PDF (Priority: P1)

**Goal**: Convert a DOCX file to PDF preserving text content, headings, and basic formatting (bold, italic, underline).

**Independent Test**: Upload a DOCX with text, headings, bold/italic formatting. Convert to PDF. Verify all text present and formatted.

### Tests for User Story 1

- [ ] T008 [P] [US1] Unit test: adapter calls `subprocess.run` with correct LibreOffice headless arguments
- [ ] T009 [P] [US1] Unit test: conversion timeout is handled (mock slow subprocess)
- [ ] T010 [P] [US1] Unit test: LibreOffice not found → `ConversionError` raised
- [ ] T011 [US1] Integration test: end-to-end conversion of real DOCX via `/convert` endpoint

### Implementation for User Story 1

- [ ] T012 [US1] Implement `supports(source, target)` — return `True` for DOCX→PDF, XLSX→PDF, PPTX→PDF
- [ ] T013 [US1] Implement `convert(source_path, target_path, options)`:
  - Build LibreOffice command: `[soffice_path, "--headless", "--convert-to", "pdf", "--outdir", output_dir, source_path]`
  - Run via `subprocess.run` with timeout
  - Parse stdout/stderr for errors
- [ ] T014 [US1] Accept "track changes" option: prepend `--infilter="Microsoft Word 2007-365 XML (.docx)"` macro to accept all changes, or add `--accept-all-changes` if available
- [ ] T015 [US1] Handle LibreOffice exit code: non-zero → parse stderr → raise `ConversionError`
- [ ] T016 [US1] Handle timeout: `subprocess.TimeoutExpired` → kill process → raise `ConversionError`
- [ ] T017 [US1] Handle LibreOffice not found: raise `ConversionError` with platform-specific install link
- [ ] T018 [US1] Move converted PDF from LibreOffice output dir to `target_path` (LibreOffice names it `{source_name}.pdf`)

**Checkpoint**: DOCX → PDF works end-to-end. Timeout and missing-LibreOffice errors are handled.

---

## Phase 4: User Story 2 - Rich Formatting Preservation (Priority: P2)

**Goal**: Verify tables, images, lists, headers, and footers survive the conversion.

**Independent Test**: Convert a DOCX with a table, image, bullet list, and header/footer. Open PDF and verify all elements.

**Note**: This user story is primarily about verification and fixing gaps. LibreOffice handles most rich formatting natively — the adapter code changes are minimal. The main work is testing.

### Tests for User Story 2

- [ ] T019 [P] [US2] Integration test: DOCX with tables → PDF has table structure
- [ ] T020 [P] [US2] Integration test: DOCX with embedded images → PDF contains images
- [ ] T021 [US2] Integration test: DOCX with headers/footers → PDF has headers/footers
- [ ] T022 [US2] Integration test: DOCX with bullet/numbered lists → PDF preserves list structure

### Implementation for User Story 2

- [ ] T023 [US2] Verify LibreOffice handles tables, images, lists, headers, footers in headless mode (test-driven)
- [ ] T024 [US2] Add missing font detection and logging: parse LibreOffice stderr for font warnings, log them
- [ ] T025 [US2] If any element is found not to render correctly, investigate and add LibreOffice CLI flags as needed

**Checkpoint**: All rich formatting elements verified to survive conversion to PDF.

---

## Phase 5: User Story 3 - XLSX and PPTX to PDF (Priority: P3)

**Goal**: Extend conversion to Excel and PowerPoint files.

**Independent Test**: Upload an XLSX table → verify readable PDF. Upload a 5-slide PPTX → verify 5-page PDF.

### Tests for User Story 3

- [ ] T026 [P] [US3] Integration test: XLSX with table data → PDF with readable table
- [ ] T027 [P] [US3] Integration test: PPTX with 5 slides → 5-page PDF
- [ ] T028 [US3] Integration test: multi-sheet XLSX → PDF contains all sheets (or active sheet)

### Implementation for User Story 3

- [ ] T029 [US3] Verify `convert()` already handles XLSX and PPTX (LibreOffice uses same `--convert-to pdf` flag). If format-specific flags are needed, parse `source_format` from the job's `FileFormat`.
- [ ] T030 [US3] For XLSX: if multi-sheet handling needs configuration, add `options["sheets"]` (e.g., "all" or a specific sheet name)
- [ ] T031 [US3] Test and fix any format-specific edge cases discovered

**Checkpoint**: All three Office formats (DOCX, XLSX, PPTX) convert to PDF correctly.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge case hardening.

- [ ] T032 Handle password-protected documents: LibreOffice may hang or error. Detect "password" in stderr → raise `ConversionError`
- [ ] T033 Handle corrupted documents: non-zero exit + specific error → raise `ConversionError`
- [ ] T034 Handle missing fonts: already logged in T024; ensure substituted text renders correctly (SC-005)
- [ ] T035 Handle OLE objects and macros: accepted as-is by LibreOffice — no special handling. Macros do not execute in headless mode.
- [ ] T036 Handle RTL text: LibreOffice handles it natively — verify with test
- [ ] T037 Add logging for conversion lifecycle (start, elapsed time, completion, errors)
- [ ] T038 Ensure temp files cleaned up after conversion (source and output from LibreOffice's working dir)
- [ ] T039 Add 3-minute timeout (configurable) for large documents

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Assumes hexagonal skeleton exists. Create adapter file + register wiring.
- **Foundational (Phase 2)**: LibreOffice detection. Blocks all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational.
  - US1 (P1): Core DOCX→PDF. No dependencies on US2 or US3.
  - US2 (P2): Rich formatting verification. Runs after US1 (tests real output).
  - US3 (P3): XLSX/PPTX support. Uses same `convert()` path as US1. Can run after US1.
- **Polish (Phase 6)**: Depends on all user stories.

### User Story Dependencies

- **User Story 1 (P1)**: Self-contained LibreOffice invocation.
- **User Story 2 (P2)**: Uses US1's convert path; adds verification tests.
- **User Story 3 (P3)**: Extends US1's supports() to include XLSX/PPTX; tests new formats.

### Within Each User Story

- Tests before implementation (except integration tests which need real LibreOffice)
- Unit tests use mocks; integration tests need LibreOffice on the test machine

## Notes

- The adapter does not bundle LibreOffice. Detection at startup + clear error at conversion time is the agreed approach.
- The same adapter (`OfficeToPdfAdapter`) handles all Office formats since they all share the same LibreOffice invocation path. This follows the hexagonal rule: one `FileConverterPort` implementation per conversion engine, not per format pair.
- `subprocess.run` with `timeout` is the primary integration point. The adapter is a thin wrapper over LibreOffice CLI.
- If the project later adds format-specific converters (e.g., python-docx → reportlab for DOCX→PDF without LibreOffice), those would be separate adapters implementing `FileConverterPort`.
