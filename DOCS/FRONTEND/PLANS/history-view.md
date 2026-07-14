# Implementation Plan: History View

**Date**: 2026-07-14
**Spec**: `DOCS/FRONTEND/SPECS/history-view.md`

## Summary

Chronological list of past conversions with filename, source/target formats, timestamp, status, and download options. Supports clearing history, deleting individual entries, and re-converting from history.

## Technical Context

**Language/Version**: TypeScript 5.x / React 18+
**Primary Dependencies**: React 18+, Zustand, TailwindCSS, date-fns (date formatting)
**Storage**: Zustand (runtime), electron-store (persisted history)
**Testing**: Vitest, React Testing Library
**Target Platform**: Electron (Windows, macOS, Linux desktop)
**Project Type**: Electron + React SPA
**Performance Goals**: Render 500 entries without noticeable lag (<300ms)
**Constraints**: History data must persist between sessions. Capped at 500 entries by default.
**Scale/Scope**: Single-user desktop app.

## Project Structure

### Documentation (this feature)

```
DOCS/FRONTEND/
├── SPECS/history-view.md
└── PLANS/history-view.md   # This file
```

### Source Code (repository root)

```
frontend/
├── src/
│   ├── interfaces/
│   │   ├── sfw/
│   │   │   └── HistoryView.tsx  # SFW History View  } THIS FEATURE
│   │   └── nsfw/
│   │       └── HistoryView.tsx  # NSFW History View } THIS FEATURE
│   ├── shared/
│   │   └── components/
│   │       ├── HistoryList.tsx    # Scrollable list of history entries
│   │       ├── HistoryEntry.tsx   # Single history entry row
│   │       └── EmptyState.tsx     # Empty state placeholder
│   └── store/
│       └── historyStore.ts       # Zustand store: persisted history entries
└── tests/
    └── unit/
        ├── HistoryView.test.tsx
        ├── HistoryList.test.tsx
        └── historyStore.test.ts
```

**Structure Decision**: This plan assumes the frontend skeleton exists. Only new view files, components, and the history store are added.

## Phase 1: Setup

**Purpose**: Create the history view files and store.

- [ ] T001 Install `date-fns` for human-readable date formatting
- [ ] T002 Create `src/store/historyStore.ts` — Zustand store with `persist` middleware using electron-store adapter (or localStorage fallback). Holds array of `HistoryEntry` objects. Actions: add, remove, clear.
- [ ] T003 Create shared components: `HistoryList.tsx`, `HistoryEntry.tsx`, `EmptyState.tsx` skeletons
- [ ] T004 Create SFW and NSFW `HistoryView.tsx` skeleton files
- [ ] T005 Add route for `/history` in `App.tsx` if not already present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify history persistence and entry creation works.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Verify `historyStore` persists entries to electron-store/localStorage across page reloads
- [ ] T007 Verify entries are ordered chronologically (most recent first)
- [ ] T008 Wire the conversion completion/failure callbacks in `conversionStore.ts` to push entries into `historyStore` (triggered after each conversion ends)
- [ ] T009 Write smoke test: `HistoryView` mounts without crash

**Checkpoint**: History entries are automatically created on conversion completion and persisted between sessions.

---

## Phase 3: User Story 1 - View Past Conversions (Priority: P1)

**Goal**: Display a chronological list of all past conversions with filename, formats, timestamp, and status.

**Independent Test**: Perform 2 conversions, open history, verify both appear with correct data.

### Tests for User Story 1

- [ ] T010 [P] [US1] Unit test: HistoryView renders list of entries from historyStore
- [ ] T011 [P] [US1] Unit test: entries show filename, source→target, timestamp, status
- [ ] T012 [P] [US1] Unit test: entries are ordered newest-first
- [ ] T013 [US1] Unit test: EmptyState renders when history is empty

### Implementation for User Story 1

- [ ] T014 [US1] Implement `HistoryEntry.tsx`: single row with filename, source_format → target_format arrow, timestamp (relative: "2 hours ago"), status badge (green for completed, red for failed)
- [ ] T015 [US1] Implement `HistoryList.tsx`: maps `historyStore.entries` to `HistoryEntry` components, virtual scrolling or lazy rendering if >100 entries
- [ ] T016 [US1] Implement `EmptyState.tsx`: icon + "No conversions yet" message + "Go to Conversion" button
- [ ] T017 [US1] Compose `HistoryView.tsx` (SFW and NSFW): TopBar + HistoryList or EmptyState
- [ ] T018 [US1] Wire `conversionStore` completion/failure to `historyStore.add()` after each conversion finishes

**Checkpoint**: History view shows all past conversions in correct order. Empty state works.

---

## Phase 4: User Story 2 - Download Converted Files (Priority: P2)

**Goal**: Offer download for completed conversions from history.

**Independent Test**: Complete a conversion, open history, click download, verify file saves.

### Tests for User Story 2

- [ ] T019 [P] [US2] Unit test: completed entry shows download button
- [ ] T020 [P] [US2] Unit test: failed entry does NOT show download button
- [ ] T021 [US2] Unit test: clicking download triggers file save or blob download
- [ ] T022 [US2] Unit test: entry with deleted/cleaned-up file shows "File no longer available" error

### Implementation for User Story 2

- [ ] T023 [US2] Add download button (icon) to completed `HistoryEntry` rows
- [ ] T024 [US2] On download click: if `output_path` is still valid, retrieve file (re-request from backend or read from local filesystem via Electron)
- [ ] T025 [US2] If output file no longer exists (temp cleaned up): show toast/error "File no longer available. Please re-convert."
- [ ] T026 [US2] Disable download button (greyed out) for entries with `failed` status

**Checkpoint**: Download from history works for completed conversions. Graceful error for missing files.

---

## Phase 5: User Story 3 - Manage History (Priority: P3)

**Goal**: Clear all history, delete individual entries, re-convert from history.

**Independent Test**: Open history with 3 entries, delete one, verify it's removed. Click clear all, verify list is empty. Click re-convert, verify navigation to conversion view.

### Tests for User Story 3

- [ ] T027 [P] [US3] Unit test: delete single entry removes it from list
- [ ] T028 [P] [US3] Unit test: clear all with confirmation removes all entries
- [ ] T029 [US3] Unit test: re-convert navigates to `/conversion` with source/target pre-filled
- [ ] T030 [US3] Unit test: clear all without confirmation does nothing (guard clause)

### Implementation for User Story 3

- [ ] T031 [US3] Add delete (trash icon) button to each `HistoryEntry` row → calls `historyStore.remove(entryId)`
- [ ] T032 [US3] Add "Clear History" button at top of history list → shows confirmation modal → calls `historyStore.clear()`
- [ ] T033 [US3] Add "Re-convert" button on each history entry → navigates to `/conversion` with state: `{ sourceFile: entry.filename, sourceFormat: entry.source_format, targetFormat: entry.target_format }`
- [ ] T034 [US3] Implement confirmation modal component (reusable) for destructive actions
- [ ] T035 [US3] Cap history store at configurable maximum (default: 500 entries) — trim oldest when exceeded

**Checkpoint**: Full history management works. Delete, clear, re-convert, and entry cap.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases and UX polish.

- [ ] T036 Handle corrupted history data in electron-store: catch parse errors, fall back to empty array, log warning
- [ ] T037 Add filter by status (All / Completed / Failed) toggle buttons
- [ ] T038 Add search/filter by filename input
- [ ] T039 Ensure SFW and NSFW variants are visually distinct
- [ ] T040 Handle rapid successive conversions not overwriting history entries (each job gets unique entry)
- [ ] T041 Ensure history view renders performantly with 500 entries (use virtualization if needed)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Assumes frontend skeleton exists. Install date-fns, create store/components.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational.
  - US1 (P1): History list display. No dependencies on US2/US3.
  - US2 (P2): Download from history. Depends on US1 (needs history entries to click on).
  - US3 (P3): History management. Depends on US1 (needs entries to delete/re-convert).
- **Polish (Phase 6)**: Depends on all user stories.

### User Story Dependencies

- **User Story 1 (P1)**: History list + store. Self-contained.
- **User Story 2 (P2)**: Adds download to US1's entries. Runs after US1.
- **User Story 3 (P3)**: Adds delete/clear/re-convert to US1's entries. Runs after US1 (can run in parallel with US2).

### Within Each User Story

- Store logic before UI components
- Tests in parallel with implementation
- SFW and NSFW variants built together

## Notes

- History entries are stored in electron-store (JSON file on disk). This is lightweight for the expected scale (<500 entries).
- The `historyStore` uses Zustand's `persist` middleware. On app load, entries are hydrated from electron-store.
- When a conversion completes in the `conversionStore`, it calls `historyStore.add()`. This coupling is intentional — both stores are part of the same frontend.
- "Re-convert" navigates to the conversion view with state. The ConversionView checks for incoming state on mount and pre-fills the source format and target format. It does not re-upload the file automatically since the temp file may have been cleaned up.
