# Feature Specification: Home View

**Created**: 2026-07-14

## User Scenarios & Testing

### User Story 1 - Landing Page with Format Cards (Priority: P1)

The user opens the app and sees a home screen with format-category cards. The PDF card is active and navigates to the conversion view. A secondary card shows "Coming Soon" and is disabled.

**Why this priority**: This is the app's entry point. Without it, the user cannot reach any conversion functionality.

**Independent Test**: Launch the app, verify two cards are visible, click the PDF card, verify it navigates to the conversion view. Click the "Coming Soon" card, verify nothing happens.

**Acceptance Scenarios**:

1. **Scenario**: App launches to home view
   - **Given** the app is opened
   - **When** the Electron window loads
   - **Then** the home view is displayed with two centered cards

2. **Scenario**: PDF card navigates to conversion
   - **Given** the user is on the home view
   - **When** the user clicks the PDF card
   - **Then** the app navigates to the conversion view

3. **Scenario**: Coming Soon card is disabled
   - **Given** the user is on the home view
   - **When** the user clicks the "Coming Soon" card with the "+" icon
   - **Then** nothing happens; the card does not respond to clicks

4. **Scenario**: Settings gear is accessible
   - **Given** the user is on the home view
   - **When** the user clicks the gear icon in the top-right corner
   - **Then** the settings view opens

5. **Scenario**: History is accessible
   - **Given** the user is on the home view
   - **When** the user clicks the history icon/button
   - **Then** the history view opens

---

### Edge Cases

- What happens if the Electron window is resized to very small dimensions? Cards should remain centered and not overflow.
- What happens if the backend is not running when the home view loads? The home view does not depend on the backend — it should display regardless.

## Requirements

### Functional Requirements

- **FR-001**: View MUST display two centered cards on the main area.
- **FR-002**: First card MUST display a PDF icon and the label "PDF", and MUST be clickable.
- **FR-003**: Clicking the PDF card MUST navigate the user to the Conversion View.
- **FR-004**: Second card MUST display a "+" icon and the label "Coming Soon", and MUST be visually disabled (greyed out, no hover effect, no click response).
- **FR-005**: View MUST display a gear icon button in the top-right corner that opens the Settings View.
- **FR-006**: View MUST display a history button/icon that opens the History View.
- **FR-007**: View MUST respect the active SFW/NSFW mode for its visual styling.

### Key Entities

- **AppRoute**: The current navigation state (home, conversion, history, settings).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Home view renders within 500ms of app launch.
- **SC-002**: Clicking the PDF card navigates to conversion view in under 200ms (no perceptible lag).
- **SC-003**: The "Coming Soon" card shows zero interactive feedback on hover or click.
