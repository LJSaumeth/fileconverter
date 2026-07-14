# Feature Specification: PDF to Image Conversion

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - Basic PDF to Image (Priority: P1)

The user uploads a PDF file and converts every page into individual image files.

**Why this priority**: This is the core conversion — without it, the feature has no value. Covers the happy path for the majority of use cases.

**Independent Test**: Upload any multi-page PDF, request conversion to PNG, verify one image per page is produced and each image is viewable.

**Acceptance Scenarios**:

1. **Scenario**: Convert a multi-page PDF to PNG images
   - **Given** a valid 3-page PDF file
   - **When** the user submits a conversion job with target format PNG
   - **Then** 3 PNG images are produced, each corresponding to one page, and all images are readable

2. **Scenario**: Convert a single-page PDF
   - **Given** a valid 1-page PDF file
   - **When** the user submits a conversion job with target format PNG
   - **Then** 1 PNG image is produced and is readable

3. **Scenario**: Convert PDF to JPG
   - **Given** a valid PDF file
   - **When** the user submits a conversion job with target format JPG
   - **Then** one JPG image per page is produced and all images are readable

---

### User Story 2 - Page Range Selection (Priority: P2)

The user can select a specific subset of pages to convert instead of the entire document.

**Why this priority**: Common real-world need (extract a single page or chapter), but the feature is usable without it since full-document conversion works.

**Independent Test**: Upload a 10-page PDF, request conversion of pages 3-5 only, verify only those 3 pages are converted.

**Acceptance Scenarios**:

1. **Scenario**: Convert a contiguous page range
   - **Given** a valid 10-page PDF file
   - **When** the user submits a conversion job with pages 3-5 and target format PNG
   - **Then** exactly 3 images are produced (pages 3, 4, 5)

2. **Scenario**: Convert a single specific page
   - **Given** a valid multi-page PDF file
   - **When** the user submits a conversion job requesting only page 1
   - **Then** exactly 1 image is produced

3. **Scenario**: Request an out-of-range page
   - **Given** a valid 5-page PDF file
   - **When** the user requests pages 6-8
   - **Then** the job fails with a clear error message indicating the page range is invalid

---

### User Story 3 - Output Quality Configuration (Priority: P3)

The user can configure output image resolution (DPI) and quality/compression level.

**Why this priority**: Useful for balancing file size vs. quality, but the feature delivers value with sensible defaults.

**Independent Test**: Convert the same PDF at 72 DPI and 300 DPI, verify the resulting images have different resolutions and the quality difference is perceptible.

**Acceptance Scenarios**:

1. **Scenario**: Convert at a specified DPI
   - **Given** a valid PDF file
   - **When** the user submits a conversion job with `{"dpi": 300}`
   - **Then** output images are rendered at 300 DPI

2. **Scenario**: Default DPI when not specified
   - **Given** a valid PDF file
   - **When** the user submits a conversion job without specifying DPI
   - **Then** output images are rendered at a reasonable default (e.g. 150 DPI)

3. **Scenario**: Convert with JPG quality setting
   - **Given** a valid PDF file
   - **When** the user requests JPG output with `{"quality": 85}`
   - **Then** output JPGs are encoded at the specified quality level

---

### Edge Cases

- **Password-protected PDF**: The adapter detects the password protection and returns a `ConversionError` with a clear message (e.g. "This PDF is password-protected and cannot be converted"). Covered by FR-007.
- **Corrupted or unreadable PDF**: The adapter captures the library-level parse error and wraps it in a `ConversionError` with a user-readable message (e.g. "The file could not be opened — it may be corrupted or not a valid PDF").
- **Empty PDF (zero pages)**: The adapter detects zero pages before rendering and returns a `ConversionError` (e.g. "The PDF contains no pages to convert").
- **Very large PDFs (500+ pages)**: The adapter processes pages sequentially and streams output to disk. If conversion exceeds a configurable timeout (default: 2 minutes), the job is marked as failed with a timeout error.
- **Reversed page range (e.g. 5-2)**: The adapter normalizes the range to ascending order (2-5) instead of treating it as an error, since the user's intent is clear.
- **Disk space runs out**: The adapter catches `OSError` during file writes and returns a `ConversionError` indicating insufficient disk space.
- **File has `.pdf` extension but is not a PDF**: The adapter's PDF library will fail to open it; this is caught and reported as a corrupted/unreadable file error.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a PDF file as input and produce one image per page as output.
- **FR-002**: System MUST support PNG and JPG as output image formats.
- **FR-003**: System MUST allow the user to specify which pages to convert via a page range.
- **FR-004**: System MUST allow the user to configure output DPI (resolution).
- **FR-005**: System MUST allow the user to configure JPG output quality (compression level).
- **FR-006**: System MUST reject invalid page ranges with a descriptive error.
- **FR-007**: System MUST handle password-protected PDFs by returning an appropriate error.
- **FR-008**: System MUST produce images that are visually faithful to the source PDF pages.
- **FR-009**: System MUST report conversion progress (current page / total pages) during processing.
- **FR-010**: System MUST deliver output as individual image files when there are 5 or fewer pages, and as a ZIP bundle when there are 6 or more pages.

### Key Entities

- **ConversionJob**: A PDF file with source format `FileFormat.PDF` and target format `FileFormat.PNG` or `FileFormat.JPG`. Options dict may include `dpi`, `quality`, and `pages` (page range).
- **ConversionResult**: Contains output paths for each generated image file, status, and any error information.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A 10-page PDF converts to 10 PNG images in under 10 seconds on a typical consumer machine.
- **SC-002**: Page range conversion produces exactly the requested pages (no off-by-one errors).
- **SC-003**: Output images at 150 DPI are visually equivalent to the source PDF when viewed at 100% zoom.
- **SC-004**: Invalid inputs (corrupted PDF, wrong page range) fail with a user-readable error message within 2 seconds.
