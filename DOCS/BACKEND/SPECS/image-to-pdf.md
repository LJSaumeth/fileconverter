# Feature Specification: Image to PDF Conversion

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - Single Image to PDF (Priority: P1)

The user uploads a single image file and converts it to a PDF document.

**Why this priority**: Core conversion path. The most common use case — a user has one image and wants it as a PDF.

**Independent Test**: Upload a PNG image, request conversion to PDF, open the resulting PDF and verify it contains the image correctly.

**Acceptance Scenarios**:

1. **Scenario**: Convert a PNG image to PDF
   - **Given** a valid PNG image file (e.g. 1920x1080)
   - **When** the user submits a conversion job with target format PDF
   - **Then** a PDF is produced containing the image, and the image fills the page

2. **Scenario**: Convert a JPG image to PDF
   - **Given** a valid JPG image file
   - **When** the user submits a conversion job with target format PDF
   - **Then** a PDF is produced containing the image correctly rendered

3. **Scenario**: Input is not a valid image
   - **Given** a file with a `.png` extension that is not actually an image
   - **When** the user submits a conversion job
   - **Then** the job fails with a clear error message indicating the file is not a valid image

---

### User Story 2 - Multiple Images to Single PDF (Priority: P2)

The user uploads multiple images and combines them into a single multi-page PDF, one image per page.

**Why this priority**: Important for document assembly, but single-image conversion provides standalone value.

**Independent Test**: Upload 3 images, convert to one PDF, verify the PDF has 3 pages with each image on a separate page.

**Acceptance Scenarios**:

1. **Scenario**: Combine multiple images into one PDF
   - **Given** three valid image files (PNG, JPG, PNG)
   - **When** the user submits a conversion job combining them into a single PDF
   - **Then** a 3-page PDF is produced with each image on its own page

2. **Scenario**: Combine images of different formats
   - **Given** one PNG and one JPG image
   - **When** the user converts both into a single PDF
   - **Then** a 2-page PDF is produced with both images correctly rendered

3. **Scenario**: Combine a single image
   - **Given** one image file in a multi-image job
   - **When** the user submits the conversion
   - **Then** a 1-page PDF is produced (same as single-image conversion)

---

### User Story 3 - Page Layout Configuration (Priority: P3)

The user can configure page size, orientation, and margins for the output PDF.

**Why this priority**: Useful for print preparation, but defaults are acceptable for most users.

**Independent Test**: Convert an image to PDF specifying A4 landscape orientation, verify the output page matches A4 landscape dimensions.

**Acceptance Scenarios**:

1. **Scenario**: Specify output page size
   - **Given** a valid image
   - **When** the user requests PDF output with `{"page_size": "A4"}`
   - **Then** the PDF page dimensions match ISO A4 (210 x 297 mm)

2. **Scenario**: Specify page orientation
   - **Given** a landscape-oriented image (1920x1080)
   - **When** the user requests PDF output with `{"orientation": "landscape"}`
   - **Then** the PDF page is in landscape orientation

3. **Scenario**: Default page size when not specified
   - **Given** a valid image
   - **When** the user submits a conversion job without page size or orientation options
   - **Then** the PDF page matches the image's natural dimensions

4. **Scenario**: Image larger than page with scaling
   - **Given** a 4000x3000 image
   - **When** the user requests A4 output with `{"fit": "inside"}`
   - **Then** the image is scaled to fit within A4 bounds while preserving aspect ratio

---

### Edge Cases

- **Corrupted or truncated image**: Pillow raises an error on open. The adapter catches it and returns a `ConversionError` (e.g. "The image file is corrupted or unreadable").
- **Very large images (e.g. 10000x10000)**: The adapter downsamples images exceeding a configurable maximum dimension (default: 5000px on the longest side) before embedding into the PDF, preserving aspect ratio. A warning is logged.
- **Image formats Pillow cannot open (e.g. HEIC, AVIF without plugins)**: The adapter rejects the file with a `ConversionError` listing the supported formats detected in the current Pillow installation. Covered by FR-008.
- **Multi-image job with zero images**: The adapter returns a validation error before processing (e.g. "At least one image must be provided").
- **Images with vastly different aspect ratios in multi-image job**: Each image is placed on its own page scaled to fit the chosen page size independently. No attempt is made to normalize aspect ratios across pages.
- **Image with transparency (alpha channel)**: The adapter composites the image onto a white background before embedding. Covered by FR-007.
- **EXIF orientation metadata**: The adapter applies EXIF orientation tags (via Pillow's `ImageOps.exif_transpose`) so rotated photos display upright in the output PDF.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept any image format supported by Pillow (PNG, JPG, BMP, TIFF, WEBP, GIF, and others) and produce a single-page PDF.
- **FR-002**: System MUST accept multiple image files and produce a multi-page PDF with one image per page.
- **FR-003**: System MUST retain the visual content of the source image without distortion or cropping by default.
- **FR-004**: System MUST allow the user to specify output page size (A4, Letter, or fit-to-image).
- **FR-005**: System MUST allow the user to specify page orientation (portrait or landscape).
- **FR-006**: System MUST preserve image aspect ratio when scaling to fit a specified page size.
- **FR-007**: System MUST handle images with transparency (alpha channel) by compositing on a white background.
- **FR-008**: System MUST reject unsupported image formats with a descriptive error.
- **FR-009**: System MUST report conversion progress during multi-image processing.

### Key Entities

- **ConversionJob**: One or more image files with source format `FileFormat.PNG` or `FileFormat.JPG` and target format `FileFormat.PDF`. Options dict may include `page_size`, `orientation`, `fit`.
- **ConversionResult**: Contains the output PDF path, status, and any error information.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A single 1920x1080 image converts to PDF in under 2 seconds.
- **SC-002**: 10 images combined into a single PDF complete in under 10 seconds.
- **SC-003**: Output PDFs open correctly in standard PDF viewers (Adobe Acrobat, browser PDF viewers).
- **SC-004**: Image content in the output PDF is visually identical to the source image at 100% zoom.
