# Implementation Plan: Image to PDF Conversion

**Date**: 2026-07-14
**Spec**: `DOCS/BACKEND/SPECS/image-to-pdf.md`

## Summary

Accept one or more image files in any Pillow-supported format and produce a PDF. Support multi-image combining (one per page), page size configuration, orientation settings, and image scaling modes.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pillow, reportlab (PDF generation)
**Storage**: tempfile + pathlib (local filesystem)
**Testing**: pytest with mocked ports
**Target Platform**: Windows, macOS, Linux (cross-platform desktop via Electron)
**Project Type**: Single backend service with hexagonal architecture
**Performance Goals**: Single image → PDF in <2 seconds; 10 images → PDF in <10 seconds
**Constraints**: All processing local. Images downsampled if exceeding 5000px on longest side. Alpha channels composited on white.
**Scale/Scope**: Single-user desktop app. No concurrent conversions in v1.

## Project Structure

### Documentation (this feature)

```
DOCS/BACKEND/
├── SPECS/image-to-pdf.md
└── PLANS/image-to-pdf.md   # This file
```

### Source Code (repository root)

```
backend/
├── adapters/
│   └── output/
│       └── converters/
│           └── image_to_pdf_adapter.py   # THIS FEATURE
├── infrastructure/
│   └── main.py                           # Wiring: register adapter
└── tests/
    ├── unit/
    │   └── test_image_to_pdf_adapter.py
    └── integration/
        └── test_image_to_pdf_e2e.py
```

**Structure Decision**: This plan assumes the hexagonal skeleton already exists (domain entities, ports, use cases, FastAPI router, storage adapter, infrastructure wiring). Only the new adapter file and its registration are added.

## Phase 1: Setup

**Purpose**: Create the adapter file and add dependencies.

- [ ] T001 Add `Pillow` and `reportlab` to `requirements.txt` if not already present
- [ ] T002 Create `backend/adapters/output/converters/image_to_pdf_adapter.py` skeleton implementing `FileConverterPort` (empty `supports()` and `convert()` methods)
- [ ] T003 Register `ImageToPdfAdapter` in `backend/infrastructure/main.py` wiring

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure the adapter is properly wired and the basic test harness exists.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Add any missing `FileFormat` entries (`FileFormat.PNG`, `FileFormat.JPG`, `FileFormat.PDF`) to `domain/entities.py`
- [ ] T005 Create `tests/unit/test_image_to_pdf_adapter.py` with a smoke test that instantiates the adapter
- [ ] T006 Verify the adapter's `supports()` returns `True` for PNG→PDF and JPG→PDF pairs, `False` for unsupported pairs

**Checkpoint**: Adapter registered, tests run, ready for implementation.

---

## Phase 3: User Story 1 - Single Image to PDF (Priority: P1)

**Goal**: Convert a single image (any Pillow-supported format) to a single-page PDF.

**Independent Test**: Upload a PNG image, convert to PDF, verify the PDF opens and contains the image.

### Tests for User Story 1

- [ ] T007 [P] [US1] Unit test: single PNG → PDF produces a valid PDF with the image
- [ ] T008 [P] [US1] Unit test: single JPG → PDF works
- [ ] T009 [P] [US1] Unit test: corrupted image raises `ConversionError`
- [ ] T010 [P] [US1] Unit test: unsupported format raises `ConversionError`
- [ ] T011 [US1] Integration test: end-to-end via `/convert` endpoint in `tests/integration/test_image_to_pdf_e2e.py`

### Implementation for User Story 1

- [ ] T012 [US1] Implement `supports(source, target)` — accept all Pillow-supported formats → PDF
- [ ] T013 [US1] Implement `convert(source_path, target_path, options)` for single-image case
- [ ] T014 [US1] Open image with Pillow, apply EXIF transpose for correct orientation
- [ ] T015 [US1] Create PDF page sized to match image dimensions using reportlab `canvas`
- [ ] T016 [US1] Draw image onto PDF page (center, fit-to-page by default)
- [ ] T017 [US1] Handle alpha channel: composite onto white background before embedding
- [ ] T018 [US1] Add error handling: wrap Pillow/reportlab errors in `ConversionError`

**Checkpoint**: Single image → PDF works for any Pillow-supported format. EXIF orientation honored. Transparency handled.

---

## Phase 4: User Story 2 - Multiple Images to PDF (Priority: P2)

**Goal**: Combine multiple images into a single multi-page PDF, one image per page.

**Independent Test**: Upload 3 images, convert to one PDF, verify 3-page output with each image on its own page.

### Tests for User Story 2

- [ ] T019 [P] [US2] Unit test: 3 images → 3-page PDF with correct image per page
- [ ] T020 [P] [US2] Unit test: images of different formats (PNG + JPG) in same PDF
- [ ] T021 [US2] Unit test: zero images in job raises `ConversionError`
- [ ] T022 [US2] Unit test: images with different aspect ratios each get their own correctly scaled page

### Implementation for User Story 2

- [ ] T023 [US2] Accept a list of source paths in the conversion job (via `ConversionJob.source_path` or options)
- [ ] T024 [US2] Iterate images in order, render each to a new PDF page
- [ ] T025 [US2] Handle mixed formats: each image opened independently with Pillow
- [ ] T026 [US2] Validate at least one image is provided before processing
- [ ] T027 [US2] Report progress per image during multi-page generation

**Checkpoint**: Multi-image → single PDF works. Mixed formats, varying aspect ratios, and zero-image edge case handled.

---

## Phase 5: User Story 3 - Page Layout Configuration (Priority: P3)

**Goal**: Users can configure page size, orientation, and image scaling mode.

**Independent Test**: Convert an image to PDF with A4 landscape, verify output matches A4 landscape dimensions.

### Tests for User Story 3

- [ ] T028 [P] [US3] Unit test: `page_size: "A4"` produces 210×297mm page
- [ ] T029 [P] [US3] Unit test: `page_size: "Letter"` produces 8.5×11in page
- [ ] T030 [P] [US3] Unit test: `orientation: "landscape"` swaps width/height
- [ ] T031 [US3] Unit test: `fit: "inside"` scales image to fit within page bounds (aspect ratio preserved)
- [ ] T032 [US3] Unit test: unspecified page size defaults to image dimensions

### Implementation for User Story 3

- [ ] T033 [US3] Parse `options["page_size"]`: support "A4", "Letter", and default image-fit
- [ ] T034 [US3] Parse `options["orientation"]`: "portrait" (default) or "landscape" (swap dimensions)
- [ ] T035 [US3] Parse `options["fit"]`: "inside" scales down to fit, none maintains original size
- [ ] T036 [US3] Implement image scaling logic: calculate scale factor to fit within page while preserving aspect ratio
- [ ] T037 [US3] Center scaled image on the page

**Checkpoint**: All layout options functional. Page size, orientation, and fit modes work correctly.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge case hardening and cleanup.

- [ ] T038 Handle very large images (>5000px): downsample before embedding, log warning
- [ ] T039 Handle EXIF orientation: already done in US1 (T014), verify all supported formats
- [ ] T040 Handle corrupted images: already done in US1 (T018), verify error message is user-readable
- [ ] T041 Handle unsupported formats: Pillow error → `ConversionError` with supported formats list
- [ ] T042 Add logging for each conversion event (start, pages generated, completion, errors)
- [ ] T043 Ensure temp files cleaned up via `FileStoragePort.cleanup()`
- [ ] T044 Add timeout handling for large multi-image jobs (default: 2 minutes)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Assumes hexagonal skeleton exists. Add Pillow/reportlab, create adapter file.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational.
  - US1 (P1): No dependencies on US2 or US3.
  - US2 (P2): Extends US1's single-image logic to multi-image. Runs after US1.
  - US3 (P3): Modifies page rendering from US1. Runs after US1 (can run in parallel with US2).
- **Polish (Phase 6)**: Depends on all user stories.

### User Story Dependencies

- **User Story 1 (P1)**: Self-contained — requires only Pillow/reportlab and the adapter skeleton.
- **User Story 2 (P2)**: Iterates the convert logic from US1 over multiple inputs.
- **User Story 3 (P3)**: Adds parameterization to the page creation from US1.

### Within Each User Story

- Tests before implementation
- Implementation: format support → open → render → error handling

## Notes

- The `convert()` signature accepts a single `source_path` (Path). For multi-image jobs, the use case or input adapter may pass a temporary directory containing all images, and `options["image_files"]` lists the ordered filenames. Alternatively, the job may include a list of paths. Clarify this during the foundational wiring in `ConverterRegistryPort`.
- reportlab `canvas` is used for PDF generation. Alternative: PyMuPDF could also be used, but reportlab is already a planned dependency and is sufficient for image embedding.
- This adapter does not touch domain or use-case code. It only implements `FileConverterPort`.
