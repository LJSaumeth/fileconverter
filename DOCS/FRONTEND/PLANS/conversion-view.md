# Implementation Plan: Conversion View

**Date**: 2026-07-14
**Spec**: `DOCS/FRONTEND/SPECS/conversion-view.md`

## Summary

Main conversion workflow: drag-and-drop file upload, auto-detect source format, select target format, configure advanced options, convert with progress tracking, and download results. Supports a conversion queue for batch processing.

## Technical Context

**Language/Version**: TypeScript 5.x / React 18+
**Primary Dependencies**: React 18+, React Dropzone, Zustand, Axios, TailwindCSS
**Storage**: Zustand (queue state, progress), electron-store (persisted defaults)
**Testing**: Vitest, React Testing Library
**Target Platform**: Electron (Windows, macOS, Linux desktop)
**Project Type**: Electron + React SPA
**Performance Goals**: Progress bar updates ≥1/sec. Queue processes 3 files sequentially without blocking UI.
**Constraints**: Backend communication via HTTP + WebSocket for progress. No file size limit enforced in frontend (backend handles validation).
**Scale/Scope**: Single-user desktop app.

## Project Structure

### Documentation (this feature)

```
DOCS/FRONTEND/
├── SPECS/conversion-view.md
└── PLANS/conversion-view.md   # This file
```

### Source Code (repository root)

```
frontend/
├── src/
│   ├── interfaces/
│   │   ├── sfw/
│   │   │   └── ConversionView.tsx  # SFW Conversion View  } THIS FEATURE
│   │   └── nsfw/
│   │       └── ConversionView.tsx  # NSFW Conversion View } THIS FEATURE
│   ├── shared/
│   │   └── components/
│   │       ├── DropZone.tsx        # Drag-and-drop area
│   │       ├── FormatSelector.tsx  # Source/target format dropdowns
│   │       ├── ProgressBar.tsx     # Animated progress bar
│   │       ├── ConversionQueue.tsx # Queue list with per-item status
│   │       ├── QueueItem.tsx       # Single queue item row
│   │       └── AdvancedOptions.tsx # Expandable options panel
│   ├── services/
│   │   └── websocket.ts           # WebSocket client for progress
│   └── store/
│       ├── conversionStore.ts     # Zustand store: queue, progress, results
│       └── settingsStore.ts       # Zustand store: persisted defaults
└── tests/
    └── unit/
        ├── ConversionView.test.tsx
        ├── DropZone.test.tsx
        ├── FormatSelector.test.tsx
        └── ConversionQueue.test.tsx
```

**Structure Decision**: This plan assumes the frontend skeleton exists (Vite, React, Tailwind, Electron, routing, mode context, API client from Home View plan). Only new view files and components are added.

## Phase 1: Setup

**Purpose**: Create the conversion view files and supporting store.

- [ ] T001 Install `react-dropzone` for drag-and-drop file handling
- [ ] T002 Create `src/store/conversionStore.ts` — Zustand store managing queue state, active jobs, progress, results
- [ ] T003 Create `src/store/settingsStore.ts` — Zustand store reading persisted defaults from electron-store/localStorage
- [ ] T004 Create `src/services/websocket.ts` — WebSocket client that connects to backend for real-time progress updates
- [ ] T005 Create shared components: `DropZone.tsx`, `FormatSelector.tsx`, `ProgressBar.tsx` skeletons
- [ ] T006 Create SFW and NSFW `ConversionView.tsx` skeleton files (render placeholder)
- [ ] T007 Add route for `/conversion` in `App.tsx` if not already present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify the conversion view plumbing works before implementing user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T008 Verify `api.get('/api/conversions')` returns supported format mappings from the backend
- [ ] T009 Verify Zustand store can hold queue items and update their state
- [ ] T010 Verify WebSocket client can connect to backend and receive progress messages
- [ ] T011 Write smoke test: `ConversionView` mounts without crash in `tests/unit/ConversionView.test.tsx`

**Checkpoint**: API client, Zustand store, and WebSocket are wired. Backend communication verified.

---

## Phase 3: User Story 1 - Basic File Conversion (Priority: P1)

**Goal**: User drops a file, selects target format, clicks convert, sees progress, downloads result.

**Independent Test**: Drop a PDF, select PNG, click convert, verify progress bar appears and output is downloadable.

### Tests for User Story 1

- [ ] T012 [P] [US1] Unit test: DropZone accepts a file and displays filename
- [ ] T013 [P] [US1] Unit test: FormatSelector shows only valid target formats for the source
- [ ] T014 [P] [US1] Unit test: clicking Convert triggers API call and shows ProgressBar
- [ ] T015 [P] [US1] Unit test: conversion failure displays error message
- [ ] T016 [US1] Integration test: full flow — drop file → select target → convert → download

### Implementation for User Story 1

- [ ] T017 [US1] Implement `DropZone.tsx`: accept drag/drop and click-to-browse, validate file extension, display file info (name, size, detected format)
- [ ] T018 [US1] Implement `FormatSelector.tsx`: fetch supported conversions from `/api/conversions`, filter targets by source, render dropdown/buttons
- [ ] T019 [US1] Implement convert flow: POST to `/api/convert` with file + source_format + target_format + options, handle response (FileResponse for success, JSON error for failure)
- [ ] T020 [US1] Implement `ProgressBar.tsx`: animated bar showing 0-100%, label text during conversion
- [ ] T021 [US1] Wire WebSocket progress: listen for `job_id` → `percentage` messages, update ProgressBar
- [ ] T022 [US1] Implement download: on success, trigger file save dialog or auto-download using the response blob
- [ ] T023 [US1] Implement error display: show error message below the progress bar or as a toast notification
- [ ] T024 [US1] Disable Convert button when no file is selected or conversion is already in progress
- [ ] T025 [US1] Create SFW and NSFW variants of ConversionView, wiring them to the same shared components

**Checkpoint**: Single file → convert → progress → download works end-to-end.

---

## Phase 4: User Story 2 - Conversion Queue (Priority: P2)

**Goal**: Add multiple files, convert them sequentially, track each file's status independently.

**Independent Test**: Add 3 PDFs, set target PNG, click Convert All, verify sequential processing with per-file progress.

### Tests for User Story 2

- [ ] T026 [P] [US2] Unit test: adding 3 files adds 3 items to the queue
- [ ] T027 [P] [US2] Unit test: removing a file from queue removes the correct item
- [ ] T028 [US2] Unit test: Convert All processes files sequentially (mock API, verify order)
- [ ] T029 [US2] Unit test: queue item status transitions: waiting → in_progress → completed/failed

### Implementation for User Story 2

- [ ] T030 [US2] Implement `ConversionQueue.tsx`: list of queue items with status indicators
- [ ] T031 [US2] Implement `QueueItem.tsx`: single row showing filename, source→target, status badge, remove (X) button, progress percentage when active
- [ ] T032 [US2] Update `conversionStore.ts` with queue logic: `addToQueue`, `removeFromQueue`, `processNext`, sequential conversion with `Promise` chain or async queue
- [ ] T033 [US2] Add "Convert All" button that processes the entire queue sequentially
- [ ] T034 [US2] Add per-file remove (X) button on queue items (disabled during conversion)
- [ ] T035 [US2] Show "Clear Queue" button to remove all non-processing items
- [ ] T036 [US2] Each queue item shows its own download button upon completion, or "Failed" badge with error tooltip

**Checkpoint**: Multi-file queue works. Sequential processing, per-file status, download per completed file.

---

## Phase 5: User Story 3 - Advanced Options per Format (Priority: P3)

**Goal**: Expandable options panel that shows format-specific controls (DPI, quality, page range, page size, orientation).

**Independent Test**: Select PDF→PNG, expand advanced options, set DPI to 300 and pages 2-5, convert, verify output.

### Tests for User Story 3

- [ ] T037 [P] [US3] Unit test: AdvancedOptions renders DPI slider and quality slider for image targets
- [ ] T038 [P] [US3] Unit test: AdvancedOptions renders page range inputs for PDF source
- [ ] T039 [P] [US3] Unit test: AdvancedOptions renders nothing for Office→PDF
- [ ] T040 [US3] Unit test: options are included in the API request payload

### Implementation for User Story 3

- [ ] T041 [US3] Implement `AdvancedOptions.tsx`: expandable panel (collapsed by default), toggle via "Advanced Options" button
- [ ] T042 [US3] PDF→Image options: DPI slider (72-600, default from settings), quality slider (1-100, JPG only), page range inputs (start, end)
- [ ] T043 [US3] Image→PDF options: page size selector (A4, Letter, fit-to-image), orientation toggle (portrait/landscape)
- [ ] T044 [US3] Office→PDF: no options (LibreOffice handles everything), show informational text
- [ ] T045 [US3] PDF→DOCX options: preserve-images toggle (default: true)
- [ ] T046 [US3] Read default values from `settingsStore.ts` and apply to option controls
- [ ] T047 [US3] Serialize options to JSON and include in the `/api/convert` POST body

**Checkpoint**: Advanced options panel works for all 4 conversion types. Defaults read from settings.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases and UX polish.

- [ ] T048 Handle backend unreachable: show "Backend unavailable" error with retry button
- [ ] T049 Handle file-size warning (>500MB): show warning message before upload
- [ ] T050 Handle unsupported file type: validate extension against supported formats list
- [ ] T051 Handle navigation-away warning: prompt user if conversion is active ("You have active conversions. Leave anyway?")
- [ ] T052 Handle timeout errors: display timeout message with suggestion to try smaller file
- [ ] T053 Handle ZIP output (≥6 pages): show download as .zip file
- [ ] T054 Add loading skeleton while fetching supported formats from backend
- [ ] T055 Ensure SFW and NSFW variants are visually distinct
- [ ] T056 Add keyboard support: Enter to confirm, Escape to cancel, Tab through options

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Assumes frontend skeleton exists (from Home View plan). Install dropzone, create store/websocket.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational.
  - US1 (P1): Core convert flow. No dependencies on US2 or US3.
  - US2 (P2): Queue logic. Depends on US1's convert API integration. Runs after US1.
  - US3 (P3): Advanced options panel. Depends on US1 for the convert flow. Can run in parallel with US2.
- **Polish (Phase 6)**: Depends on all user stories.

### User Story Dependencies

- **User Story 1 (P1)**: DropZone + FormatSelector + convert + download. Self-contained beyond shared infra.
- **User Story 2 (P2)**: Wraps US1's convert call in a queue with sequential processing.
- **User Story 3 (P3)**: Adds options panel that modifies the convert payload. Independent of US2.

### Within Each User Story

- Shared components before view assembly
- Tests in parallel with implementation
- SFW and NSFW variants built together (same logic, different Tailwind classes)

## Notes

- React Dropzone handles both drag-and-drop and click-to-browse — no separate file input needed.
- WebSocket progress updates are optional enhancement. If WebSocket fails to connect, fall back to polling or show indeterminate progress during conversion.
- The Zustand `conversionStore` is the single source of truth for queue state. Components read from it; actions mutate it.
- Backend returns a file blob on success. Use `URL.createObjectURL` or `electron.dialog.showSaveDialog` to offer download.
