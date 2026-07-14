# Implementation Plan: PDF to DOCX Conversion

**Date**: 2026-07-14
**Spec**: `DOCS/BACKEND/SPECS/pdf-to-docx.md`

## Summary

Accept text-based PDFs and produce editable DOCX files using the pdf2docx library. Preserve text content, font sizes, alignment, paragraph structure, and images. For image-only PDFs, embed pages as images. OCR adapter structure created but implementation deferred.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pdf2docx
**Storage**: tempfile + pathlib (local filesystem)
**Testing**: pytest with mocked ports and real pdf2docx for integration
**Target Platform**: Windows, macOS, Linux (cross-platform desktop via Electron)
**Project Type**: Single backend service with hexagonal architecture
**Performance Goals**: 10-page text-only PDF → DOCX in <10 seconds
**Constraints**: All processing local. RTL text and multi-column layouts are known limitations. 3-minute timeout. Deferred: OCR for scanned PDFs.
**Scale/Scope**: Single-user desktop app.

## Project Structure

### Documentation (this feature)

```
DOCS/BACKEND/
├── SPECS/pdf-to-docx.md
└── PLANS/pdf-to-docx.md   # This file
```

### Source Code (repository root)

```
backend/
├── adapters/
│   └── output/
│       └── converters/
│           ├── pdf_to_docx_adapter.py       # THIS FEATURE (main)
│           └── pdf_to_docx_ocr_adapter.py   # Skeleton only (deferred)
├── infrastructure/
│   └── main.py                             # Wiring: register adapters
└── tests/
    ├── unit/
    │   ├── test_pdf_to_docx_adapter.py
    │   └── test_pdf_to_docx_ocr_adapter.py   # Skeleton smoke test only
    └── integration/
        └── test_pdf_to_docx_e2e.py
```

**Structure Decision**: This plan assumes the hexagonal skeleton already exists. Two adapter files are created: the main adapter (implemented) and the OCR adapter (skeleton only, per FR-007).

## Phase 1: Setup

**Purpose**: Create adapter files and add dependencies.

- [ ] T001 Add `pdf2docx` to `requirements.txt`
- [ ] T002 Create `backend/adapters/output/converters/pdf_to_docx_adapter.py` skeleton implementing `FileConverterPort`
- [ ] T003 Create `backend/adapters/output/converters/pdf_to_docx_ocr_adapter.py` skeleton implementing `FileConverterPort` with `supports()` returning `True` for PDF→DOCX but `convert()` raising `NotImplementedError` with docstring noting deferred implementation
- [ ] T004 Register both adapters in `backend/infrastructure/main.py` wiring
- [ ] T005 Add `FileFormat.DOCX` to `domain/entities.py` if not already present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure pdf2docx is importable and the adapter wiring is correct.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Verify pdf2docx imports successfully (post-install smoke test)
- [ ] T007 Create `tests/unit/test_pdf_to_docx_adapter.py` with smoke test: instantiate adapter, verify `supports(FileFormat.PDF, FileFormat.DOCX)` is `True`
- [ ] T008 Create `tests/unit/test_pdf_to_docx_ocr_adapter.py` with smoke test: instantiate OCR adapter, verify `supports()` returns `True` and `convert()` raises `NotImplementedError`
- [ ] T009 Verify wiring in `main.py`: `ConverterRegistryPort.get_converter(FileFormat.PDF, FileFormat.DOCX)` returns the main adapter (not OCR)

**Checkpoint**: Adapters registered, pdf2docx available, tests run.

---

## Phase 3: User Story 1 - Basic PDF to DOCX (Priority: P1)

**Goal**: Convert a text-based PDF to an editable DOCX, preserving all text content.

**Independent Test**: Upload a text-based PDF with paragraphs and headings. Convert to DOCX. Open in Word/LibreOffice and verify all text is present and editable.

### Tests for User Story 1

- [ ] T010 [P] [US1] Unit test: text-only single-page PDF → DOCX with searchable text
- [ ] T011 [P] [US1] Unit test: multi-page PDF → DOCX with all pages' text
- [ ] T012 [P] [US1] Unit test: corrupted/unreadable PDF raises `ConversionError`
- [ ] T013 [P] [US1] Unit test: image-only PDF (no text layer) → gracefully handles (embeds page images)
- [ ] T014 [US1] Integration test: end-to-end via `/convert` endpoint with real text PDF

### Implementation for User Story 1

- [ ] T015 [US1] Implement `supports(source, target)` — return `True` for PDF→DOCX
- [ ] T016 [US1] Implement `convert(source_path, target_path, options)` using pdf2docx:
  - `from pdf2docx import Converter`
  - `cv = Converter(source_path)`
  - `cv.convert(target_path, start=0, end=None)`  (full document)
  - `cv.close()`
- [ ] T017 [US1] Detect text layer: if pdf2docx extracts no text (or very little text relative to page count), determine if PDF is image-only
- [ ] T018 [US1] For image-only PDFs: embed each page as an image in the DOCX (using PyMuPDF for page→image extraction, then inserting into DOCX via python-docx). Fallback strategy per FR-006.
- [ ] T019 [US1] Handle pdf2docx import error: if library not installed, raise `ConversionError` with install instructions
- [ ] T020 [US1] Wrap pdf2docx errors in `ConversionError` with user-readable messages
- [ ] T021 [US1] Report progress: per-page status via `ProgressNotifierPort`

**Checkpoint**: Text-based PDF → editable DOCX works. Image-only PDFs get embedded page images. Errors handled.

---

## Phase 4: User Story 2 - Layout and Formatting Preservation (Priority: P2)

**Goal**: Preserve font sizes, text alignment, paragraph spacing, and embedded images in the output DOCX.

**Independent Test**: Convert a PDF with mixed fonts, centered text, and images. Verify DOCX preserves formatting.

### Tests for User Story 2

- [ ] T022 [P] [US2] Unit test: font sizes preserved (relative hierarchy at minimum)
- [ ] T023 [P] [US2] Unit test: text alignment preserved (left, center, right)
- [ ] T024 [P] [US2] Unit test: paragraph breaks and spacing reflected in output
- [ ] T025 [US2] Integration test: PDF with mixed formatting → DOCX with formatting preserved

### Implementation for User Story 2

- [ ] T026 [US2] pdf2docx handles most formatting natively. Verify and tune parameters:
  - Check that `cv.convert()` preserves font sizes, alignment, and spacing by default
  - If not, investigate pdf2docx configuration options
- [ ] T027 [US2] Add `options["preserve_images"]` flag (default: `True`). When enabled, ensure pdf2docx extracts and places images.
- [ ] T028 [US2] For elements that pdf2docx does not preserve, document as known limitations in the adapter docstring

**Checkpoint**: Output DOCX preserves the major formatting elements from the source PDF.

---

## Phase 5: User Story 3 - Scanned/Image-Based PDF Handling (Priority: P3)

**Goal**: Provide graceful handling for image-only PDFs. Embed pages as images. OCR adapter skeleton ready for future.

**Independent Test**: Upload a scanned PDF (no text). Convert. Verify output DOCX contains each page as an embedded image.

### Tests for User Story 3

- [ ] T029 [P] [US3] Unit test: 3-page scanned PDF → DOCX with 3 embedded page images
- [ ] T030 [P] [US3] Unit test: OCR adapter skeleton exists, `convert()` raises `NotImplementedError` with clear message
- [ ] T031 [US3] Integration test: scanned PDF via `/convert` → DOCX opens with embedded images

### Implementation for User Story 3

- [ ] T032 [US3] Image-only detection already implemented in US1 (T017). Verify it correctly identifies scanned PDFs.
- [ ] T033 [US3] Enhance image-embedding fallback (from T018): use higher DPI for embedded images (200 DPI default), maintain page order
- [ ] T034 [US3] Ensure OCR adapter skeleton has proper docstring: documents that OCR implementation (Tesseract) is a future phase, describes expected interface
- [ ] T035 [US3] Document the decision: for now, scanned PDFs produce image-embedded DOCX. OCR availability is logged at startup but does not block conversion.

**Checkpoint**: Scanned PDFs handled gracefully. OCR adapter structure ready for future implementation.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge case hardening and known limitation documentation.

- [ ] T036 Handle password-protected PDFs: pdf2docx will fail to open → catch and raise `ConversionError`
- [ ] T037 Handle embedded font differences: pdf2docx maps to standard DOCX fonts — document that exact font matching is not guaranteed
- [ ] T038 Handle complex vector graphics/charts: text extraction may be partial — embed as images where possible
- [ ] T039 Handle RTL text: pdf2docx has limited RTL support — document as known limitation in adapter docstring
- [ ] T040 Handle multi-column layouts: pdf2docx extracts in reading order — known limitation, document
- [ ] T041 Handle form fields: pdf2docx extracts filled values as text — document that interactive elements are lost
- [ ] T042 Add 3-minute timeout for large PDFs
- [ ] T043 Add logging for conversion lifecycle
- [ ] T044 Ensure temp files cleaned up

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Assumes hexagonal skeleton exists. Add pdf2docx, create adapters.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational.
  - US1 (P1): Core pdf2docx conversion. No dependencies on US2/US3.
  - US2 (P2): Formatting verification. Runs after US1.
  - US3 (P3): Scanned PDF handling. Runs after US1 (needs image-embedding from T018).
- **Polish (Phase 6)**: Depends on all user stories.

### User Story Dependencies

- **User Story 1 (P1)**: Self-contained pdf2docx integration.
- **User Story 2 (P2)**: Uses US1's convert output; verifies formatting fidelity.
- **User Story 3 (P3)**: Uses US1's image-only detection; builds on fallback strategy.

### Within Each User Story

- Tests before implementation
- Implementation: supports() → convert() → text-layer detection → fallback → error handling

## Notes

- pdf2docx may have limitations with complex PDFs. The adapter should document which PDF features are known to be poorly supported.
- The OCR adapter skeleton exists to satisfy FR-007: the structure is ready for Tesseract integration in a future phase without refactoring the converter registry.
- PyMuPDF is used indirectly: for image-only PDF fallback (page → image extraction) if pdf2docx can't extract text. If PyMuPDF is already a dependency from pdf-to-image, no new dependency is added.
- The adapter is a thin wrapper over pdf2docx. Domain logic (validation, orchestration) lives in the use case, not here.
