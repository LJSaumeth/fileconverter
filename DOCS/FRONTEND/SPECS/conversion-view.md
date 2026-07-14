# Feature Specification: Conversion View

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - Basic File Conversion (Priority: P1)

The user drags or selects a file, chooses a target format, clicks convert, and receives the converted file. Progress is shown during conversion.

**Why this priority**: This is the core value of the application. All other views support this workflow.

**Independent Test**: Drop a PDF, select PNG as target, click convert, verify progress bar appears, verify the converted PNG downloads or is offered for save.

**Acceptance Scenarios**:

1. **Scenario**: Drag and drop a file
   - **Given** the user is on the conversion view
   - **When** the user drags a PDF file onto the drop zone
   - **Then** the file is accepted, the source format is auto-detected, and the file info is displayed

2. **Scenario**: Select target format and convert
   - **Given** a file has been dropped and source format is detected
   - **When** the user selects a target format from the dropdown and clicks "Convert"
   - **Then** a conversion request is sent to the backend, a progress indicator appears, and the converted file is offered for download upon completion

3. **Scenario**: Conversion fails gracefully
   - **Given** a file has been submitted for conversion
   - **When** the backend returns an error (e.g. unsupported format, corrupted file)
   - **Then** the error message is displayed to the user in a clear, readable format

4. **Scenario**: No file selected before convert
   - **Given** the user has not dropped or selected a file
   - **When** the user clicks "Convert"
   - **Then** the button is disabled or shows a validation message

---

### User Story 2 - Conversion Queue (Priority: P2)

The user can add multiple files to a queue and convert them sequentially, with individual progress per file.

**Why this priority**: Important for power users converting multiple files, but single-file conversion is independently usable.

**Independent Test**: Add 3 PDFs to the queue, set target to PNG for all, click "Convert All", verify each file converts in sequence with progress updates.

**Acceptance Scenarios**:

1. **Scenario**: Add multiple files to queue
   - **Given** the user is on the conversion view
   - **When** the user drops 3 files onto the drop zone
   - **Then** all 3 files appear in a queue list with their detected source formats

2. **Scenario**: Convert queue sequentially
   - **Given** 3 files are in the queue with a target format set
   - **When** the user clicks "Convert All"
   - **Then** files convert one at a time, each showing its own progress, and downloading independently upon completion

3. **Scenario**: Remove file from queue
   - **Given** files are in the queue
   - **When** the user clicks the remove (X) button on a queued file
   - **Then** that file is removed from the queue

4. **Scenario**: Queue shows status per file
   - **Given** files are converting in the queue
   - **When** the user observes the queue
   - **Then** each file shows its status (waiting, converting with progress %, completed, failed)

---

### User Story 3 - Advanced Options per Format (Priority: P3)

The user can configure format-specific options before converting (DPI, quality, page range, page size, orientation).

**Why this priority**: Adds quality control, but sensible defaults handle the primary use case.

**Independent Test**: Drop a PDF, expand advanced options, set DPI to 300, set page range 2-5, convert, verify output matches settings.

**Acceptance Scenarios**:

1. **Scenario**: PDF to Image options panel
   - **Given** a PDF file is loaded and PNG target is selected
   - **When** the user expands "Advanced Options"
   - **Then** DPI slider, quality slider, and page range inputs are shown

2. **Scenario**: Image to PDF options panel
   - **Given** a PNG file is loaded and PDF target is selected
   - **When** the user expands "Advanced Options"
   - **Then** page size selector and orientation toggle are shown

3. **Scenario**: Office to PDF options panel
   - **Given** a DOCX file is loaded and PDF target is selected
   - **When** the user expands "Advanced Options"
   - **Then** minimal or no options are shown (LibreOffice handles most formatting natively)

4. **Scenario**: PDF to DOCX options panel
   - **Given** a PDF file is loaded and DOCX target is selected
   - **When** the user expands "Advanced Options"
   - **Then** preserve-images toggle is shown

---

### Edge Cases

- What happens when the backend is not reachable? Display a "Backend unavailable" error with instructions to restart the app.
- What happens when the user drops a file larger than 500MB? Show a file-size warning and reject it.
- What happens when the user drops an unsupported file type? Show a validation message listing supported formats.
- What happens when the user navigates away during an active conversion? Warn them that the conversion will be lost.
- What happens when the conversion times out? Show a timeout error with a suggestion to try a smaller file.
- What happens if the output is a ZIP (≥6 pages)? Offer the ZIP file for download with a clear label.

## Requirements

### Functional Requirements

- **FR-001**: View MUST provide a drag-and-drop zone for file upload and a click-to-browse fallback.
- **FR-002**: View MUST auto-detect the source format based on file extension upon file selection.
- **FR-003**: View MUST display only target formats supported for the detected source format (filtered from the backend's `/conversions` endpoint).
- **FR-004**: View MUST show a progress bar during active conversion (percentage 0-100).
- **FR-005**: View MUST allow adding multiple files to a queue for sequential processing.
- **FR-006**: View MUST show per-file status in the queue (waiting, converting, completed, failed).
- **FR-007**: View MUST allow removing files from the queue before conversion starts.
- **FR-008**: View MUST provide an expandable "Advanced Options" panel with format-specific controls (DPI, quality, page range, page size, orientation).
- **FR-009**: View MUST offer the output file for download upon conversion completion.
- **FR-010**: View MUST display clear error messages for conversion failures, including backend-unreachable, timeout, unsupported format, and corrupted file.
- **FR-011**: View MUST warn the user if they attempt to navigate away during an active conversion.
- **FR-012**: View MUST display the settings gear icon in the top-right corner at all times.
- **FR-013**: View MUST display a back button to return to the Home View.
- **FR-014**: View MUST respect the active SFW/NSFW mode for its visual styling.

### Key Entities

- **ConversionQueueItem**: A file entry in the queue (id, filename, source_format, target_format, status, progress, error_message, output_url).
- **FormatOption**: A configurable option for a conversion (name, type, min, max, default, applicable_formats).

## Success Criteria

### Measurable Outcomes

- **SC-001**: File drop is acknowledged within 200ms with visual feedback (highlight, file info).
- **SC-002**: Progress bar updates at least once per second during active conversion.
- **SC-003**: Queue processes 3 files sequentially without requiring user intervention between files.
- **SC-004**: Advanced options panel toggles its content in under 100ms based on selected source/target pair.
- **SC-005**: Error messages are displayed within 1 second of receiving an error response from the backend.
