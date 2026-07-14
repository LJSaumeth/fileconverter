# Implementation Plan: PDF to Image Conversion

**Date**: 2026-07-14
**Spec**: `DOCS/BACKEND/SPECS/pdf-to-image.md`

## Summary

Accept a PDF file and produce images (PNG/JPG), one per page. Support page range selection, DPI configuration, and JPG quality control. Output ≤5 pages as individual files, ≥6 pages as a ZIP bundle.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyMuPDF (fitz)
**Storage**: tempfile + pathlib (local filesystem)
**Testing**: pytest with mocked ports
**Target Platform**: Windows, macOS, Linux (cross-platform desktop via Electron)
**Project Type**: Single backend service with hexagonal architecture
**Performance Goals**: 10-page PDF → 10 images in <10 seconds
**Constraints**: All processing local (no network calls). Images rendered at configurable DPI. Disk space usage proportional to output image size.
**Scale/Scope**: Single-user desktop app. No concurrent conversions needed in v1.

## Project Structure

### Documentation (this feature)

```
DOCS/BACKEND/
├── SPECS/pdf-to-image.md
└── PLANS/pdf-to-image.md   # This file
```

### Source Code (repository root)

```
backend/
├── domain/
│   ├── entities.py              # ConversionJob, FileFormat, ConversionResult, ConversionProgress
│   └── ports/
│       ├── input/
│       │   ├── convert_file_use_case.py
│       │   └── list_supported_conversions_use_case.py
│       └── output/
│           ├── file_converter_port.py
│           ├── converter_registry_port.py
│           ├── file_storage_port.py
│           └── progress_notifier_port.py
├── application/
│   └── use_cases/
│       ├── convert_file.py
│       └── list_supported_conversions.py
├── adapters/
│   ├── input/
│   │   ├── http/
│   │   │   └── conversion_router.py
│   │   └── websocket/
│   │       └── progress_websocket.py
│   └── output/
│       ├── converters/
│       │   └── pdf_to_image_adapter.py   # THIS FEATURE
│       └── storage/
│           └── local_file_storage_adapter.py
├── infrastructure/
│   ├── config.py
│   └── main.py                     # wiring + FastAPI app
└── tests/
    ├── unit/
    │   └── test_pdf_to_image_adapter.py
    └── integration/
        └── test_pdf_to_image_e2e.py
```

**Structure Decision**: This is the first feature. It includes the shared hexagonal skeleton (domain, application, infrastructure) since no code exists yet. Subsequent feature plans assume this skeleton is already in place.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python project and create the hexagonal architecture skeleton.

- [ ] T001 Create `backend/` directory with `requirements.txt` and `pyproject.toml`
- [ ] T002 Add dependencies: `PyMuPDF`, `fastapi`, `uvicorn`, `python-multipart`, `websockets`, `python-dotenv`, `loguru`
- [ ] T003 Add dev dependencies: `pytest`, `pytest-asyncio`, `coverage`, `ruff`, `mypy`
- [ ] T004 Create `backend/domain/entities.py` with `FileFormat`, `ConversionStatus`, `ConversionJob`, `ConversionResult`, `ConversionProgress`
- [ ] T005 Create `backend/domain/ports/output/` with `FileConverterPort`, `ConverterRegistryPort`, `FileStoragePort`, `ProgressNotifierPort`
- [ ] T006 Create `backend/domain/ports/input/` with `ConvertFileUseCase`, `ListSupportedConversionsUseCase`
- [ ] T007 Create `backend/application/use_cases/convert_file.py` implementing `ConvertFileUseCase`
- [ ] T008 Create `backend/application/use_cases/list_supported_conversions.py` implementing `ListSupportedConversionsUseCase`
- [ ] T009 Create `backend/adapters/output/storage/local_file_storage_adapter.py` implementing `FileStoragePort`
- [ ] T010 Create `backend/adapters/input/http/conversion_router.py` with FastAPI `/convert` and `/conversions` endpoints
- [ ] T011 Create `backend/infrastructure/config.py` (env loading via python-dotenv, defaults)
- [ ] T012 Create `backend/infrastructure/main.py` with FastAPI app creation, dependency wiring, and uvicorn entrypoint
- [ ] T013 Configure ruff and mypy in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Everything the pdf-to-image adapter depends on before implementing conversion logic.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T014 Create `backend/adapters/output/converters/pdf_to_image_adapter.py` skeleton implementing `FileConverterPort` (empty `supports()` and `convert()` methods)
- [ ] T015 Register `PdfToImageAdapter` in `backend/infrastructure/main.py` wiring (add it to `ConverterRegistry`)
- [ ] T016 Add `FileFormat.PNG` and `FileFormat.JPG` entries to `entities.py` (if not already present)
- [ ] T017 Create `backend/adapters/output/converters/` package `__init__.py`
- [ ] T018 Create `backend/adapters/output/storage/` package `__init__.py`
- [ ] T019 Write a smoke test in `tests/unit/test_pdf_to_image_adapter.py` that instantiates the adapter and asserts `supports(FileFormat.PDF, FileFormat.PNG)` returns `True`

**Checkpoint**: Adapter skeleton is wired, tests pass, project structure is solid. User stories can now begin.

---

## Phase 3: User Story 1 - Basic PDF to Image (Priority: P1)

**Goal**: Convert a full multi-page PDF to one image per page (PNG and JPG).

**Independent Test**: Upload a 3-page PDF, request PNG conversion, verify 3 viewable PNG images are produced.

### Tests for User Story 1

- [ ] T020 [P] [US1] Unit test: `convert()` produces correct number of images for a multi-page PDF in `tests/unit/test_pdf_to_image_adapter.py`
- [ ] T021 [P] [US1] Unit test: `convert()` works for a single-page PDF
- [ ] T022 [P] [US1] Integration test: end-to-end conversion via FastAPI endpoint in `tests/integration/test_pdf_to_image_e2e.py`

### Implementation for User Story 1

- [ ] T023 [US1] Implement `supports(source, target)` to return `True` for PDF→PNG and PDF→JPG pairs
- [ ] T024 [US1] Implement `convert(source_path, target_path, options)` using PyMuPDF: open PDF, iterate pages, render each to PNG/JPG
- [ ] T025 [US1] Handle output file naming: `{original_name}_page_{n}.{ext}` per page
- [ ] T026 [US1] Handle output delivery: ≤5 pages → individual files, ≥6 pages → ZIP bundle (uses `zipfile` stdlib)
- [ ] T027 [US1] Wire conversion progress reporting: emit `ConversionProgress` per page via injected `ProgressNotifierPort`
- [ ] T028 [US1] Add error handling: wrap PyMuPDF errors in `ConversionError` with user-readable messages

**Checkpoint**: Full PDF → images conversion works. Single and multi-page PDFs convert correctly. Progress is reported.

---

## Phase 4: User Story 2 - Page Range Selection (Priority: P2)

**Goal**: Allow users to convert a specific subset of pages instead of the entire document.

**Independent Test**: Upload a 10-page PDF, request pages 3-5, verify exactly 3 images (pages 3, 4, 5).

### Tests for User Story 2

- [ ] T029 [P] [US2] Unit test: page range option converts only specified pages
- [ ] T030 [P] [US2] Unit test: reversed page range (5-2) is normalized to ascending (2-5)
- [ ] T031 [US2] Unit test: out-of-range page numbers raise `ConversionError`

### Implementation for User Story 2

- [ ] T032 [US2] Parse `options["pages"]` in `convert()` — accept a tuple `(start, end)` or list `[2, 5]` for individual pages
- [ ] T033 [US2] Normalize reversed ranges: if `start > end`, swap them
- [ ] T034 [US2] Validate page range against document page count; raise `ConversionError` if out of bounds
- [ ] T035 [US2] Only iterate selected pages during conversion loop

**Checkpoint**: Page range selection works. Errors for invalid ranges are clear.

---

## Phase 5: User Story 3 - Quality Configuration (Priority: P3)

**Goal**: Users can configure output DPI and JPG compression quality.

**Independent Test**: Convert same PDF at 72 DPI and 300 DPI, verify output images differ in resolution.

### Tests for User Story 3

- [ ] T036 [P] [US3] Unit test: DPI option produces correctly sized images (page inches × DPI = pixel dimensions)
- [ ] T037 [P] [US3] Unit test: JPG quality option is passed through to PyMuPDF render
- [ ] T038 [US3] Unit test: unspecified DPI defaults to 150

### Implementation for User Story 3

- [ ] T039 [US3] Parse `options["dpi"]` — default to 150 if absent, clamp to valid range (72–600)
- [ ] T040 [US3] Pass DPI to PyMuPDF `page.get_pixmap(dpi=dpi)`
- [ ] T041 [US3] For JPG output: parse `options["quality"]` (1–100), default to 85, pass to image save

**Checkpoint**: Quality and DPI configuration fully functional. All user stories complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge case hardening and cleanup.

- [ ] T042 Handle password-protected PDFs: catch PyMuPDF auth error → raise `ConversionError`
- [ ] T043 Handle corrupted/unreadable PDFs: catch PyMuPDF open error → raise `ConversionError`
- [ ] T044 Handle empty PDFs (zero pages): check `doc.page_count == 0` before processing → raise `ConversionError`
- [ ] T045 Handle disk-full errors: catch `OSError` during file write → raise `ConversionError`
- [ ] T046 Handle files with `.pdf` extension that aren't valid PDFs: caught by corrupted-PDF handler (T043)
- [ ] T047 Add timeout for very large PDFs: track elapsed time, raise `ConversionError` if exceeded (default: 2 minutes)
- [ ] T048 Add logging for each conversion event (start, progress, completion, error) via `loguru`
- [ ] T049 Ensure temp files are cleaned up after conversion (success or failure) via `FileStoragePort.cleanup()`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — creates entire project from scratch.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - US1 (P1): No dependencies on US2 or US3.
  - US2 (P2): Depends on US1's convert loop. Runs after US1.
  - US3 (P3): Depends on US1's rendering code. Runs after US2 (or in parallel with US2 since it touches different code paths).
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Requires `convert()` loop to exist (Phase 2 provides skeleton).
- **User Story 2 (P2)**: Adds page filtering to the convert loop from US1.
- **User Story 3 (P3)**: Adds option parsing to the render call from US1.

### Within Each User Story

- Tests before implementation
- Implementation: supports() → convert() → error handling → progress reporting

## Notes

- This plan includes the shared hexagonal architecture skeleton (Phase 1). When later features are implemented, their Phase 1 will be much lighter — just creating the adapter file.
- PyMuPDF uses the AGPL license. Confirm this is acceptable for the project.
- The adapter never touches domain logic (entities, use cases). It only implements `FileConverterPort` and is called by the use case.
- Dependency injection in `infrastructure/main.py` means the adapter is swappable without changing any other file.
