# Implementation Plan: Settings View

**Date**: 2026-07-14
**Spec**: `DOCS/FRONTEND/SPECS/settings-view.md`

## Summary

Settings panel accessible from the gear icon on every view. Provides SFW/NSFW mode toggle with persistence, default conversion preferences (DPI, quality, page size), backend connection status indicator, and reset-to-defaults functionality.

## Technical Context

**Language/Version**: TypeScript 5.x / React 18+
**Primary Dependencies**: React 18+, Zustand, TailwindCSS
**Storage**: electron-store (persisted settings), Zustand (runtime)
**Testing**: Vitest, React Testing Library
**Target Platform**: Electron (Windows, macOS, Linux desktop)
**Project Type**: Electron + React SPA
**Performance Goals**: Mode toggle applies within 100ms. Settings persist between launches.
**Constraints**: Settings must be readable from other views (conversion view reads default options). Backend status checked periodically.
**Scale/Scope**: Single-user desktop app.

## Project Structure

### Documentation (this feature)

```
DOCS/FRONTEND/
├── SPECS/settings-view.md
└── PLANS/settings-view.md   # This file
```

### Source Code (repository root)

```
frontend/
├── src/
│   ├── interfaces/
│   │   ├── sfw/
│   │   │   └── SettingsView.tsx  # SFW Settings View  } THIS FEATURE
│   │   └── nsfw/
│   │       └── SettingsView.tsx  # NSFW Settings View } THIS FEATURE
│   ├── shared/
│   │   └── components/
│   │       ├── ModeToggle.tsx      # SFW/NSFW switch component
│   │       ├── SettingsSlider.tsx  # Reusable slider for numeric settings
│   │       ├── SettingsSelect.tsx  # Reusable dropdown for option settings
│   │       └── BackendStatus.tsx   # Connection status indicator
│   ├── store/
│   │   └── settingsStore.ts       # Zustand store (already exists from Conversion View plan, extended here)
│   └── services/
│       └── api.ts                 # Extended with healthCheck function
└── tests/
    └── unit/
        ├── SettingsView.test.tsx
        ├── ModeToggle.test.tsx
        └── settingsStore.test.ts
```

**Structure Decision**: This plan assumes the frontend skeleton exists. The `settingsStore.ts` was created in the Conversion View plan; this plan extends it with full settings management.

## Phase 1: Setup

**Purpose**: Create settings view files and extend the settings store.

- [ ] T001 Create shared components: `ModeToggle.tsx`, `SettingsSlider.tsx`, `SettingsSelect.tsx`, `BackendStatus.tsx` skeletons
- [ ] T002 Create SFW and NSFW `SettingsView.tsx` skeleton files
- [ ] T003 Extend `src/store/settingsStore.ts` with full settings state: `mode`, `defaultDpi`, `defaultQuality`, `defaultPageSize`, `maxHistoryEntries`, actions: `setMode`, `setDefaultDpi`, `setDefaultQuality`, `setDefaultPageSize`, `resetDefaults`
- [ ] T004 Add `healthCheck()` function to `src/services/api.ts`: GET request to backend root or a `/health` endpoint
- [ ] T005 Add route for `/settings` in `App.tsx` if not already present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify settings store persistence and mode toggling works globally.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Verify `settingsStore.mode` toggling updates `AppModeContext` and applies the correct CSS class
- [ ] T007 Verify settings persist across page reloads (electron-store integration)
- [ ] T008 Verify `healthCheck()` returns a valid response when backend is running
- [ ] T009 Write smoke test: `SettingsView` mounts without crash

**Checkpoint**: Settings store wired to mode context, persistence verified, health check functional.

---

## Phase 3: User Story 1 - Toggle SFW/NSFW Mode (Priority: P1)

**Goal**: Toggle switches the entire app between SFW and NSFW visual themes, persists across sessions.

**Independent Test**: Toggle NSFW → verify whole app changes visually. Relaunch → verify NSFW persists.

### Tests for User Story 1

- [ ] T010 [P] [US1] Unit test: ModeToggle dispatches `setMode` action to settingsStore
- [ ] T011 [P] [US1] Unit test: mode change updates AppModeContext
- [ ] T012 [P] [US1] Unit test: mode persists to electron-store/localStorage
- [ ] T013 [US1] Unit test: first launch (no persisted setting) defaults to SFW

### Implementation for User Story 1

- [ ] T014 [US1] Implement `ModeToggle.tsx`: labeled toggle switch with "SFW" / "NSFW" labels, reads current mode from `settingsStore.mode`, calls `settingsStore.setMode()` on toggle
- [ ] T015 [US1] Wire `settingsStore.setMode()` to also update `AppModeContext` so the entire app re-renders with the correct theme
- [ ] T016 [US1] On app mount, hydrate `settingsStore` from electron-store; default to `"sfw"` if no persisted value exists
- [ ] T017 [US1] Ensure the mode applies to ALL views immediately — verify by navigating between views after toggling

**Checkpoint**: Mode toggle works globally and persists across app restarts.

---

## Phase 4: User Story 2 - Default Conversion Preferences (Priority: P2)

**Goal**: Set default DPI, quality, and page size that pre-fill the conversion view's advanced options.

**Independent Test**: Set default DPI to 300, go to conversion view → PDF to PNG, expand advanced options → verify DPI shows 300.

### Tests for User Story 2

- [ ] T018 [P] [US2] Unit test: SettingsSlider updates settingsStore value
- [ ] T019 [P] [US2] Unit test: SettingsSelect updates settingsStore value
- [ ] T020 [P] [US2] Unit test: resetDefaults restores factory defaults
- [ ] T021 [US2] Unit test: conversion view reads default DPI from settingsStore

### Implementation for User Story 2

- [ ] T022 [US2] Implement `SettingsSlider.tsx`: labeled slider with min/max/step/value/unit display. Used for DPI (72-600) and quality (1-100).
- [ ] T023 [US2] Implement `SettingsSelect.tsx`: labeled dropdown selector. Used for page size (A4, Letter).
- [ ] T024 [US2] DPI setting: bind to `settingsStore.defaultDpi`, slider 72-600, step 10, show current value
- [ ] T025 [US2] Quality setting: bind to `settingsStore.defaultQuality`, slider 1-100, step 5, show current value
- [ ] T026 [US2] Page size setting: bind to `settingsStore.defaultPageSize`, dropdown with Options: A4, Letter
- [ ] T027 [US2] Max history entries setting: bind to `settingsStore.maxHistoryEntries`, number input 100-1000
- [ ] T028 [US2] Implement "Reset to Defaults" button: confirmation modal → calls `settingsStore.resetDefaults()` with factory values
- [ ] T029 [US2] Wire conversion view's `AdvancedOptions` to read defaults from `settingsStore`

**Checkpoint**: All default preferences configurable in settings and respected by conversion view.

---

## Phase 5: User Story 3 - Backend Status (Priority: P3)

**Goal**: Show whether the backend is reachable with a live connection indicator.

**Independent Test**: Open settings with backend running → green "Connected". Stop backend → wait → red "Disconnected".

### Tests for User Story 3

- [ ] T030 [P] [US3] Unit test: BackendStatus shows "Connected" when health check succeeds
- [ ] T031 [P] [US3] Unit test: BackendStatus shows "Disconnected" when health check fails
- [ ] T032 [US3] Unit test: health check is called periodically (mocked timer)

### Implementation for User Story 3

- [ ] T033 [US3] Implement `BackendStatus.tsx`: status dot (green/red), label ("Connected" / "Disconnected"), last-checked timestamp
- [ ] T034 [US3] Use `setInterval` (5 seconds) to call `api.healthCheck()` — update status state on success/failure
- [ ] T035 [US3] Clean up interval on component unmount
- [ ] T036 [US3] Show backend port and URL in a small info section for debugging
- [ ] T037 [US3] On first connection failure, attempt one immediate retry before showing "Disconnected"

**Checkpoint**: Backend status indicator works in real time. Periodic check, cleanup on unmount.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases and UX polish.

- [ ] T038 Handle corrupted persisted settings: catch JSON parse errors in hydrate, fall back to factory defaults, log warning
- [ ] T039 Handle electron-store unavailable (running outside Electron): fall back to localStorage with a warning log
- [ ] T040 Handle backend port change: store the current port and use it for health checks
- [ ] T041 Add visual feedback on settings change: brief highlight or confirmation toast when a setting is saved
- [ ] T042 Ensure SFW and NSFW variants of settings view are visually distinct
- [ ] T043 "Reset to Defaults" should not reset the SFW/NSFW mode preference

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Assumes frontend skeleton exists. Extend store, create components.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational.
  - US1 (P1): Mode toggle. No dependencies on US2/US3.
  - US2 (P2): Default preferences. Depends on US1 for store structure. Can run in parallel with US3.
  - US3 (P3): Backend status. Independent of US2 — runs after US1.
- **Polish (Phase 6)**: Depends on all user stories.

### User Story Dependencies

- **User Story 1 (P1)**: Mode toggle + persistence. Self-contained.
- **User Story 2 (P2)**: Preference controls. Uses same store as US1. Can run in parallel.
- **User Story 3 (P3)**: Backend status. Uses API client. Can run in parallel with US2.

### Within Each User Story

- Store logic before UI components
- Tests in parallel with implementation
- SFW and NSFW variants built together

## Notes

- The `settingsStore` is the central source of truth. It uses Zustand's `persist` middleware to sync to electron-store. Other stores (conversionStore, historyStore) read from it for default values.
- The mode toggle is the most critical settings feature. It must work even if the settings store fails to load (fall back to SFW).
- Backend health check uses a lightweight endpoint. If the backend doesn't expose `/health`, use the `/api/conversions` endpoint as a connectivity probe.
- Settings view is accessible via the gear icon in the TopBar, which is present on every view. No navigation guard needed — settings can be opened and closed at any time without affecting active conversions.
