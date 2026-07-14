# Feature Specification: History View

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - View Past Conversions (Priority: P1)

The user opens the history view and sees a chronological list of all past conversions with their status, source/target formats, and date.

**Why this priority**: Core history value — users need to find and access past conversions. Without the list, the view is empty.

**Independent Test**: Perform 2-3 conversions, open history, verify all conversions are listed with correct filenames, formats, dates, and statuses.

**Acceptance Scenarios**:

1. **Scenario**: History shows completed conversions
   - **Given** the user has completed 2 conversions (PDF→PNG, JPG→PDF)
   - **When** the user opens the history view
   - **Then** both conversions are listed with filename, source→target, timestamp, and "Completed" status

2. **Scenario**: History shows failed conversions
   - **Given** the user attempted a conversion that failed
   - **When** the user opens the history view
   - **Then** the failed conversion is listed with "Failed" status and the error message is visible

3. **Scenario**: Empty history state
   - **Given** no conversions have been performed
   - **When** the user opens the history view
   - **Then** an empty-state message is displayed (e.g. "No conversions yet")

---

### User Story 2 - Download Converted Files (Priority: P2)

The user can download the output file from any completed conversion in the history.

**Why this priority**: History without download access has limited utility. The user must be able to retrieve their converted files.

**Independent Test**: Complete a conversion, open history, click download on the entry, verify the file is offered for download/save.

**Acceptance Scenarios**:

1. **Scenario**: Download a completed conversion
   - **Given** a conversion entry with status "Completed" in the history
   - **When** the user clicks the download button/icon on that entry
   - **Then** the output file is offered for download

2. **Scenario**: Download unavailable for failed conversions
   - **Given** a conversion entry with status "Failed" in the history
   - **When** the user views the entry
   - **Then** the download button is disabled or not shown

3. **Scenario**: Downloaded file is no longer available
   - **Given** a conversion entry that was completed but the temp file has been cleaned up
   - **When** the user clicks download
   - **Then** an error message is shown ("File no longer available. Please reconvert.")

---

### User Story 3 - Manage History (Priority: P3)

The user can clear all history entries or re-convert a file from history.

**Why this priority**: Quality-of-life feature. The core history and download functions are usable without it.

**Acceptance Scenarios**:

1. **Scenario**: Clear all history
   - **Given** the history contains multiple entries
   - **When** the user clicks "Clear History" and confirms
   - **Then** all history entries are removed

2. **Scenario**: Re-convert from history
   - **Given** a failed or completed conversion in history
   - **When** the user clicks "Re-convert" on that entry
   - **Then** the app navigates to the conversion view with the same source file and target format pre-selected

3. **Scenario**: Delete single entry
   - **Given** the history contains multiple entries
   - **When** the user clicks delete (trash icon) on a specific entry
   - **Then** only that entry is removed from history

---

### Edge Cases

- What happens when the history grows very large (1000+ entries)? Paginate or use virtual scrolling, and cap storage at a configurable maximum (e.g. 500 entries).
- What happens when a history entry references a temp file that was cleaned up? Show "File no longer available" as handled in US2 scenario 3.
- What happens when the user clears history while a conversion is in progress? The active conversion is not affected; only stored history entries are cleared.
- What happens when localStorage/electron-store data is corrupted? Gracefully handle by showing an empty history and logging a warning.

## Requirements

### Functional Requirements

- **FR-001**: View MUST display a chronological list of all past conversions (most recent first).
- **FR-002**: Each history entry MUST show filename, source format, target format, timestamp, and status (completed/failed).
- **FR-003**: View MUST show an empty-state message when no history entries exist.
- **FR-004**: Completed entries MUST offer a download button to retrieve the output file.
- **FR-005**: Failed entries MUST display the error message from the conversion.
- **FR-006**: View MUST allow clearing all history entries with a confirmation prompt.
- **FR-007**: View MUST allow deleting individual history entries.
- **FR-008**: View MUST allow re-converting from a history entry (navigates to conversion view with file pre-loaded).
- **FR-009**: History data MUST persist between app sessions via electron-store or localStorage.
- **FR-010**: View MUST cap history at a configurable maximum number of entries (default: 500).
- **FR-011**: View MUST display the settings gear icon in the top-right corner at all times.
- **FR-012**: View MUST display a back button to return to the Home View.
- **FR-013**: View MUST respect the active SFW/NSFW mode for its visual styling.

### Key Entities

- **HistoryEntry**: A record of a past conversion (id, job_id, filename, source_format, target_format, timestamp, status, error_message, output_path).

## Success Criteria

### Measurable Outcomes

- **SC-001**: History view renders within 300ms even with 500 entries.
- **SC-002**: Download of a completed file initiates within 500ms of clicking the download button.
- **SC-003**: Clear history operation completes within 200ms with visual feedback.
- **SC-004**: History persists correctly between app restarts (entries survive a quit and relaunch).
