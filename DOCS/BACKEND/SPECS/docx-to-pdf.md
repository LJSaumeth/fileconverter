# Feature Specification: DOCX to PDF Conversion

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - Basic DOCX to PDF (Priority: P1)

The user uploads a DOCX file and converts it to a PDF while preserving text content, basic formatting, and document structure.

**Why this priority**: Core conversion — the minimum viable feature. Covers the most common use case.

**Independent Test**: Upload a simple DOCX with text, headings, and paragraphs, convert to PDF, verify the output contains all text and headings in the correct order.

**Acceptance Scenarios**:

1. **Scenario**: Convert a simple text DOCX to PDF
   - **Given** a valid DOCX file containing text, paragraphs, and headings
   - **When** the user submits a conversion job with target format PDF
   - **Then** a PDF is produced containing all text content, with headings distinguishable from body text

2. **Scenario**: Convert a DOCX with basic formatting
   - **Given** a valid DOCX file containing bold, italic, and underlined text
   - **When** the user submits a conversion job
   - **Then** the output PDF preserves bold, italic, and underline formatting

3. **Scenario**: Input is not a valid DOCX
   - **Given** a file with a `.docx` extension that is corrupted or not a valid Office document
   - **When** the user submits a conversion job
   - **Then** the job fails with a clear error message indicating the file is invalid

---

### User Story 2 - Rich Formatting Preservation (Priority: P2)

The user converts a DOCX that contains tables, images, lists, and headers/footers, expecting these elements to appear in the output PDF.

**Why this priority**: Many real-world documents contain these elements. Without it, conversion of professional documents is incomplete.

**Independent Test**: Upload a DOCX containing a table, an embedded image, bullet lists, and a header, convert to PDF, verify all elements are present.

**Acceptance Scenarios**:

1. **Scenario**: Convert DOCX with tables
   - **Given** a DOCX containing a 3x3 table with cell borders and text
   - **When** the user submits a conversion job
   - **Then** the output PDF contains a table with the same structure and cell content

2. **Scenario**: Convert DOCX with embedded images
   - **Given** a DOCX containing an embedded PNG image
   - **When** the user submits a conversion job
   - **Then** the output PDF contains the image positioned correctly relative to surrounding text

3. **Scenario**: Convert DOCX with numbered and bulleted lists
   - **Given** a DOCX containing both numbered and bulleted lists
   - **When** the user submits a conversion job
   - **Then** the output PDF preserves the list structure, numbering, and bullet styles

4. **Scenario**: Convert DOCX with headers and footers
   - **Given** a DOCX containing a header with page numbers and a footer
   - **When** the user submits a conversion job
   - **Then** the output PDF includes the header and footer on each page

---

### User Story 3 - XLSX and PPTX to PDF (Priority: P3)

The user can also convert Excel (XLSX) and PowerPoint (PPTX) files to PDF, not just Word documents.

**Why this priority**: Extends the feature to the full Office suite, but DOCX is the highest-demand format.

**Independent Test**: Upload an XLSX with a table, convert to PDF, verify the table is readable. Upload a PPTX with 3 slides, convert to PDF, verify all 3 slides appear.

**Acceptance Scenarios**:

1. **Scenario**: Convert an XLSX spreadsheet to PDF
   - **Given** a valid XLSX file containing data in multiple columns and rows
   - **When** the user submits a conversion job with target format PDF
   - **Then** a PDF is produced containing the spreadsheet data in a readable layout

2. **Scenario**: Convert a PPTX presentation to PDF
   - **Given** a valid PPTX file with 5 slides containing text and images
   - **When** the user submits a conversion job
   - **Then** a 5-page PDF is produced with each slide rendered on its own page

3. **Scenario**: Convert a multi-sheet XLSX
   - **Given** an XLSX file with 3 sheets
   - **When** the user submits a conversion job
   - **Then** the output PDF contains data from all sheets (or the active sheet, depending on configuration)

---

### Edge Cases

- **Password-protected document**: LibreOffice will prompt for a password in headless mode. The adapter passes no password and intercepts the resulting error, returning a `ConversionError` (e.g. "This document is password-protected and cannot be converted"). Covered by FR-007.
- **Fonts not installed on the system**: LibreOffice substitutes missing fonts with available fallbacks. The adapter logs a warning for each missing font but conversion proceeds. Covered by SC-005.
- **Very large documents (100+ pages DOCX, 10000+ rows XLSX)**: The adapter processes the document via LibreOffice with no special handling; large documents will simply take longer. If conversion exceeds a configurable timeout (default: 3 minutes), the job fails.
- **Embedded OLE objects or macros**: LibreOffice renders OLE objects as static images in the output PDF if the host application is available; otherwise they appear as placeholder icons. Macros do not execute. No special handling required.
- **Track changes or comments present**: LibreOffice renders the document in its current visible state. The adapter will apply an option to accept all changes before export if feasible, to avoid markup clutter in the PDF.
- **Right-to-left (RTL) text**: LibreOffice handles RTL natively. No special handling required on the adapter side.
- **LibreOffice not installed**: The adapter detects the missing binary at startup and returns a `ConversionError` with platform-specific install instructions. Covered by FR-006.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a DOCX file and produce a PDF that preserves text content and basic formatting (bold, italic, underline).
- **FR-002**: System MUST preserve document structure including tables, lists, headers, and footers in the output PDF.
- **FR-003**: System MUST preserve embedded images from the source document in the output PDF.
- **FR-004**: System MUST accept XLSX files and produce a readable PDF of the spreadsheet data.
- **FR-005**: System MUST accept PPTX files and produce a PDF with one page per slide.
- **FR-006**: System MUST detect whether LibreOffice is installed on the host system at startup by checking common install paths per platform (Windows: `C:\Program Files\LibreOffice\program\soffice.exe`, macOS: `/Applications/LibreOffice.app/Contents/MacOS/soffice`, Linux: `libreoffice` on PATH). If not found, the adapter MUST raise a clear error with instructions for the user to install LibreOffice.
- **FR-007**: System MUST return a descriptive error for password-protected documents.
- **FR-008**: System MUST report conversion progress during processing.
- **FR-009**: System MUST produce valid PDFs that open in standard PDF viewers.

### Key Entities

- **ConversionJob**: An Office document with source format `FileFormat.DOCX`, `FileFormat.XLSX`, or `FileFormat.PPTX` and target format `FileFormat.PDF`. Options dict is empty or may include format-specific settings.
- **ConversionResult**: Contains the output PDF path, status, and any error information.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A 20-page text-only DOCX converts to PDF in under 15 seconds.
- **SC-002**: Output PDF text is selectable and searchable (not a flat image).
- **SC-003**: Tables and lists in the output PDF preserve the same row/column structure and indentation as the source.
- **SC-004**: A 10-slide PPTX converts to a 10-page PDF in under 15 seconds.
- **SC-005**: Missing font glyphs are substituted with a fallback font rather than producing blank spaces.
