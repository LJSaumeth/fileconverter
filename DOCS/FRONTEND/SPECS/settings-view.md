# Feature Specification: Settings View

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - Toggle SFW/NSFW Mode (Priority: P1)

The user toggles between SFW (safe-for-work, professional appearance) and NSFW (not-safe-for-work, uninhibited appearance) modes. The preference persists between sessions.

**Why this priority**: This is the defining feature of the dual-mode UI. Must work from day one since both modes are built from the start.

**Independent Test**: Toggle from SFW to NSFW, verify the entire app's visual theme changes immediately. Close and reopen the app, verify the NSFW mode persists.

**Acceptance Scenarios**:

1. **Scenario**: Toggle from SFW to NSFW
   - **Given** the app is in SFW mode
   - **When** the user opens settings and toggles the mode switch to NSFW
   - **Then** the entire app's visual styling changes to the NSFW theme immediately

2. **Scenario**: Toggle from NSFW to SFW
   - **Given** the app is in NSFW mode
   - **When** the user opens settings and toggles the mode switch to SFW
   - **Then** the entire app's visual styling changes to the SFW theme immediately

3. **Scenario**: Mode persists between sessions
   - **Given** the app was closed while in NSFW mode
   - **When** the user relaunches the app
   - **Then** the app opens in NSFW mode

4. **Scenario**: First launch defaults to SFW
   - **Given** the app is launched for the first time (no persisted preference)
   - **When** the home view loads
   - **Then** the app displays in SFW mode

---

### User Story 2 - Default Conversion Preferences (Priority: P2)

The user can set default values for conversion options that apply to all new conversion jobs.

**Why this priority**: Saves users from repeatedly setting the same options. Useful but the app works without it.

**Independent Test**: Set default DPI to 300 in settings, start a new PDF→PNG conversion, verify the advanced options panel shows DPI pre-set to 300.

**Acceptance Scenarios**:

1. **Scenario**: Set default image DPI
   - **Given** the user is in settings
   - **When** the user sets the default DPI slider to 300 and saves
   - **Then** all new PDF→image conversions default to 300 DPI

2. **Scenario**: Set default image quality
   - **Given** the user is in settings
   - **When** the user sets the default JPG quality to 90 and saves
   - **Then** all new conversions to JPG default to quality 90

3. **Scenario**: Reset to factory defaults
   - **Given** the user has changed several default options
   - **When** the user clicks "Reset to Defaults" and confirms
   - **Then** all settings return to their factory default values

---

### User Story 3 - Backend Status (Priority: P3)

The user can see whether the backend is running and view its connection status.

**Why this priority**: Diagnostic aid. Users can troubleshoot connection issues without restarting blindly.

**Independent Test**: Open settings while backend is running, verify status shows "Connected". Stop the backend server, verify status changes to "Disconnected".

**Acceptance Scenarios**:

1. **Scenario**: Backend is running and reachable
   - **Given** the Python backend process is running
   - **When** the user opens settings
   - **Then** the backend status section shows "Connected" with a green indicator

2. **Scenario**: Backend is unreachable
   - **Given** the Python backend process is not running or has crashed
   - **When** the user opens settings
   - **Then** the backend status section shows "Disconnected" with a red indicator

3. **Scenario**: Backend status updates in real time
   - **Given** the backend is running and status shows "Connected"
   - **When** the backend process stops
   - **Then** the status changes to "Disconnected" within a few seconds

---

### Edge Cases

- What happens when the persisted settings are corrupted? Fall back to factory defaults and log a warning.
- What happens if localStorage/electron-store is unavailable? Use in-memory defaults for the current session.
- What happens when the backend port changes between sessions? The status check should use the current port from electron-store or re-discover it.

## Requirements

### Functional Requirements

- **FR-001**: View MUST provide a toggle/switch to change between SFW and NSFW modes.
- **FR-002**: Mode change MUST take effect immediately across all views.
- **FR-003**: Mode preference MUST be persisted via electron-store (or localStorage as fallback) and restored on app launch.
- **FR-004**: View MUST provide configurable default values for conversion options: default DPI (72–600), default JPG quality (1–100), default page size (A4, Letter).
- **FR-005**: View MUST provide a "Reset to Defaults" button that restores all settings to factory values with a confirmation prompt.
- **FR-006**: View MUST display the backend connection status (Connected/Disconnected) with a visual indicator.
- **FR-007**: Backend status MUST be periodically checked (every 5 seconds) and updated in real time.
- **FR-008**: View MUST gracefully handle corrupted persisted settings by falling back to defaults.
- **FR-009**: View MUST display a back button to return to the previous view.
- **FR-010**: The settings gear icon MUST be present in the top-right corner of every view AND always open this settings view when clicked.
- **FR-011**: View MUST respect the active SFW/NSFW mode for its own visual styling.

### Key Entities

- **AppSettings**: Persisted preferences (mode: "sfw"|"nsfw", default_dpi: int, default_quality: int, default_page_size: str, max_history_entries: int).
- **BackendStatus**: Current backend state (connected: bool, port: int, last_checked: timestamp).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Mode toggle takes effect across the entire app within 100ms of switching.
- **SC-002**: Settings persist correctly between app restarts (verified by relaunch test).
- **SC-003**: Backend status indicator correctly reflects connectivity within 5 seconds of a change.
- **SC-004**: Reset to Defaults operation completes and reflects in the UI within 200ms.
