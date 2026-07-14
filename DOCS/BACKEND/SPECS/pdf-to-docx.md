# Feature Specification: PDF to DOCX Conversion

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - Basic PDF to DOCX (Priority: P1)

The user uploads a text-based PDF and converts it to an editable DOCX file, preserving the text content.

**Why this priority**: Core conversion path. The primary reason users want PDF-to-DOCX is to edit content locked in a PDF.

**Independent Test**: Upload a text-based PDF with paragraphs and headings, convert to DOCX, open it in Word/LibreOffice and verify all text is present and editable.

**Acceptance Scenarios**:

1. **Scenario**: Convert a text-based PDF to DOCX
   - **Given** a valid text-based PDF containing paragraphs and headings
   - **When** the user submits a conversion job with target format DOCX
   - **Then** a DOCX file is produced containing all the text, and the text is editable in a word processor

2. **Scenario**: Convert PDF with multiple text blocks
   - **Given** a PDF with text distributed across multiple blocks/areas on each page
   - **When** the user submits a conversion job
   - **Then** the output DOCX contains all text blocks, ordered in a readable flow

3. **Scenario**: Input is not a valid PDF
   - **Given** a file with a `.pdf` extension that is corrupted or not actually a PDF
   - **When** the user submits a conversion job
   - **Then** the job fails with a clear error message indicating the file is invalid

---

### User Story 2 - Layout and Formatting Preservation (Priority: P2)

The user converts a PDF and expects the output DOCX to preserve as much of the original layout and formatting as possible — font sizes, text alignment, spacing, and paragraph structure.

**Why this priority**: Significantly improves the quality of the editable output, reducing manual reformatting work.

**Independent Test**: Convert a PDF with mixed font sizes, centered text, and bullet lists, verify the DOCX preserves these formatting elements.

**Acceptance Scenarios**:

1. **Scenario**: Preserve font sizes and styles
   - **Given** a PDF containing text in 12pt, 18pt (headings), and 10pt (footnotes)
   - **When** the user submits a conversion job
   - **Then** the output DOCX preserves the relative font size hierarchy

2. **Scenario**: Preserve text alignment
   - **Given** a PDF containing left-aligned, centered, and right-aligned paragraphs
   - **When** the user submits a conversion job
   - **Then** the output DOCX preserves the alignment of each paragraph

3. **Scenario**: Preserve line spacing and paragraph breaks
   - **Given** a PDF with clear paragraph separations and consistent line spacing
   - **When** the user submits a conversion job
   - **Then** the output DOCX reflects the paragraph structure and spacing of the source

4. **Scenario**: Document with mixed content types
   - **Given** a PDF containing text, tables, and images
   - **When** the user submits a conversion job
   - **Then** the output DOCX contains the text as editable content, and images are placed near their original positions

---

### User Story 3 - Scanned/Image-Based PDF Handling (Priority: P3)

The user uploads a scanned PDF (each page is an image with no embedded text) and the system extracts text via OCR if possible, or produces a DOCX with the page images embedded.

**Why this priority**: Many PDFs are scanned documents. Without OCR, this feature is limited to text-based PDFs only.

**Independent Test**: Upload a scanned PDF (image-only pages), request conversion, verify the output DOCX either contains OCR-extracted text or embedded page images.

**Acceptance Scenarios**:

1. **Scenario**: Detect an image-based PDF
   - **Given** a scanned PDF with no extractable text layer
   - **When** the user submits a conversion job
   - **Then** the system identifies that the PDF has no text layer and applies the appropriate strategy

2. **Scenario**: OCR extraction from scanned PDF
   - **Given** a scanned PDF with clear printed text (300 DPI minimum)
   - **When** the user submits a conversion job with OCR enabled
   - **Then** the output DOCX contains the extracted text with reasonable accuracy

3. **Scenario**: Scanned PDF without OCR
   - **Given** a scanned PDF
   - **When** the user submits a conversion job without OCR (or OCR is not available)
   - **Then** the output DOCX contains each page embedded as an image

---

### Edge Cases

- **Password-protected PDF**: The adapter detects password protection and returns a `ConversionError`. Covered by FR-008.
- **PDFs with embedded fonts not on the system**: The pdf2docx library maps extracted text to standard DOCX fonts. Embedded fonts may cause slight formatting differences but text content is preserved.
- **Very large PDFs (500+ pages)**: The adapter processes pages sequentially. If conversion exceeds a configurable timeout (default: 3 minutes), the job fails with a timeout error.
- **Complex vector graphics or charts**: Text from charts and vector graphics may not be extractable. These elements are captured as embedded images in the output DOCX where possible.
- **Right-to-left (RTL) text**: The pdf2docx library has limited RTL support. Text content is preserved but text direction may not be correctly applied. This is a known limitation documented in the adapter.
- **Multi-column layouts**: The pdf2docx library extracts text in reading order. Multi-column layouts may produce interleaved text where column boundaries are not preserved. This is a known limitation.
- **PDF with form fields**: Form field content (filled values) is extracted as regular text. Interactive form elements themselves are lost; only the filled values are preserved.
- **pdf2docx library not installed or incompatible**: The adapter checks for pdf2docx at import time. If unavailable, it raises a clear error instructing the user (or developer) to install the dependency.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a text-based PDF and produce an editable DOCX file.
- **FR-002**: System MUST preserve text content, font size hierarchy, and text alignment from the source PDF.
- **FR-003**: System MUST preserve paragraph structure and line spacing where detectable.
- **FR-004**: System MUST place images from the source PDF into the output DOCX near their original positions.
- **FR-005**: System MUST detect whether the input PDF has an extractable text layer.
- **FR-006**: System MUST embed page images into the output DOCX for image-only PDFs as a fallback.
- **FR-007**: The adapter structure for OCR-based extraction (e.g. Tesseract) MUST exist in the codebase (`backend/adapters/output/converters/pdf_to_docx_ocr_adapter.py`) but its implementation is deferred to a future phase.
- **FR-008**: System MUST return a descriptive error for password-protected PDFs.
- **FR-009**: System MUST produce DOCX files that open correctly in Microsoft Word and LibreOffice Writer.
- **FR-010**: System MUST report conversion progress during processing.

### Key Entities

- **ConversionJob**: A PDF file with source format `FileFormat.PDF` and target format `FileFormat.DOCX`. Options dict may include `ocr` (boolean) and `preserve_images` (boolean).
- **ConversionResult**: Contains the output DOCX path, status, and any error information.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A 10-page text-only PDF converts to DOCX in under 10 seconds.
- **SC-002**: All text from the source PDF is present in the output DOCX (100% text extraction rate for text-based PDFs).
- **SC-003**: Output DOCX opens as an editable document in Microsoft Word and LibreOffice Writer without errors.
- **SC-004**: Font size hierarchy is correctly preserved for at least 90% of text elements in the output.
