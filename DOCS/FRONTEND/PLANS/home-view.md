# Implementation Plan: Home View

**Date**: 2026-07-14
**Spec**: `DOCS/FRONTEND/SPECS/home-view.md`

## Summary

Landing screen with two centered cards: an active PDF card that navigates to the Conversion View, and a disabled "Coming Soon" card with a "+" icon. Includes a gear icon (Settings) and history button in the top bar. This is the first frontend plan and includes the full project scaffolding.

## Technical Context

**Language/Version**: TypeScript 5.x / React 18+
**Primary Dependencies**: React 18+, Vite, TailwindCSS, React Router, Zustand, Axios
**Storage**: electron-store (persisted settings), Zustand (runtime state)
**Testing**: Vitest (unit), React Testing Library (components)
**Target Platform**: Electron (Windows, macOS, Linux desktop)
**Project Type**: Electron + React SPA
**Performance Goals**: Home view renders within 500ms of launch
**Constraints**: 100% local — no external CDN or cloud dependencies at runtime. SFW/NSFW themes must apply immediately.
**Scale/Scope**: Single-user desktop app, 4 views.

## Project Structure

### Documentation (this feature)

```
DOCS/FRONTEND/
├── SPECS/home-view.md
└── PLANS/home-view.md   # This file
```

### Source Code (repository root)

```
frontend/
├── package.json
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── index.html
├── src/
│   ├── main.tsx                    # React entry point
│   ├── App.tsx                     # Root component, routing, mode context
│   ├── interfaces/
│   │   ├── sfw/
│   │   │   ├── HomeView.tsx       # SFW Home View  } THIS FEATURE
│   │   │   ├── ConversionView.tsx
│   │   │   ├── HistoryView.tsx
│   │   │   └── SettingsView.tsx
│   │   └── nsfw/
│   │       ├── HomeView.tsx       # NSFW Home View  } THIS FEATURE
│   │       ├── ConversionView.tsx
│   │       ├── HistoryView.tsx
│   │       └── SettingsView.tsx
│   ├── shared/
│   │   ├── components/
│   │   │   ├── TopBar.tsx          # Gear icon + History button + Back button
│   │   │   └── Card.tsx           # Reusable card component
│   │   └── icons/
│   │       ├── PdfIcon.tsx
│   │       ├── PlusIcon.tsx
│   │       ├── GearIcon.tsx
│   │       └── HistoryIcon.tsx
│   ├── context/
│   │   └── AppModeContext.tsx      # SFW/NSFW mode provider
│   ├── services/
│   │   └── api.ts                 # Axios client, health check, conversion requests
│   └── types/
│       └── index.ts               # Shared TypeScript types
├── electron/
│   ├── main.ts                    # Electron main process
│   └── preload.ts                 # Preload script
└── tests/
    ├── unit/
    │   └── HomeView.test.tsx
    └── setup.ts
```

**Structure Decision**: This is the first frontend feature. It includes the full project scaffolding (Vite, React, Tailwind, Electron, routing, mode context, API client) since nothing exists yet. Each view gets separate SFW and NSFW implementations under `interfaces/`. Subsequent plans assume this skeleton exists and only add their view files.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the frontend project and Electron shell.

- [ ] T001 Create `frontend/` directory with `npm init` / `package.json`
- [ ] T002 Install dependencies: `react`, `react-dom`, `react-router-dom`, `zustand`, `axios`, `tailwindcss`, `@tailwindcss/vite`
- [ ] T003 Install dev dependencies: `vite`, `@vitejs/plugin-react`, `typescript`, `@types/react`, `vitest`, `@testing-library/react`, `jsdom`
- [ ] T004 Create `vite.config.ts` with React plugin and TailwindCSS plugin
- [ ] T005 Create `tsconfig.json` with strict mode
- [ ] T006 Create `tailwind.config.ts` with SFW and NSFW theme extensions
- [ ] T007 Create `index.html` entry point
- [ ] T008 Create `src/main.tsx` with React root render
- [ ] T009 Create `src/App.tsx` with routing (home → conversion → history → settings) using React Router
- [ ] T010 Create `src/types/index.ts` with shared types (FileFormat, ConversionStatus, AppMode, etc.)
- [ ] T011 Create `src/context/AppModeContext.tsx` with SFW/NSFW mode state and toggle function, persisted via electron-store or localStorage
- [ ] T012 Create `src/services/api.ts` with Axios instance, health check, and conversion request functions
- [ ] T013 Create Electron shell in `electron/main.ts` (create window, load Vite dev server or built files)
- [ ] T014 Create `electron/preload.ts`
- [ ] T015 Create shared components: `TopBar.tsx` (gear icon + history button + back button), `Card.tsx`
- [ ] T016 Create icon components: `PdfIcon.tsx`, `PlusIcon.tsx`, `GearIcon.tsx`, `HistoryIcon.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure routing, mode switching, and the top bar work before building the home view.

**⚠️ CRITICAL**: No home view work can begin until this phase is complete.

- [ ] T017 Verify Vite dev server starts and renders a blank React app
- [ ] T018 Verify Electron launches and loads the React app in a window
- [ ] T019 Verify routing works: navigating between `/home`, `/conversion`, `/history`, `/settings` renders placeholder text
- [ ] T020 Verify mode toggle in `AppModeContext` switches between SFW and NSFW and applies a CSS class to the root element
- [ ] T021 Verify `TopBar` renders gear icon (→ `/settings`) and history icon (→ `/history`) and back button (→ `/home`)
- [ ] T022 Write smoke test: `HomeView` renders without crashing in `tests/unit/HomeView.test.tsx`

**Checkpoint**: App skeleton functional — Electron window loads, routing works, mode toggles, TopBar visible.

---

## Phase 3: User Story 1 - Landing Page with Format Cards (Priority: P1)

**Goal**: Render two centered cards. PDF card is clickable and navigates to `/conversion`. "Coming Soon" card is disabled.

**Independent Test**: Launch app, verify two cards centered on screen. Click PDF card → navigates to conversion. Click "Coming Soon" card → nothing happens.

### Tests for User Story 1

- [ ] T023 [P] [US1] Unit test: HomeView renders two cards in `tests/unit/HomeView.test.tsx`
- [ ] T024 [P] [US1] Unit test: clicking PDF card calls navigation to `/conversion`
- [ ] T025 [P] [US1] Unit test: "Coming Soon" card has no onClick handler and shows disabled styling
- [ ] T026 [US1] Unit test: GearIcon in TopBar navigates to `/settings`
- [ ] T027 [US1] Unit test: HistoryIcon in TopBar navigates to `/history`

### Implementation for User Story 1

- [ ] T028 [US1] Create `src/interfaces/sfw/HomeView.tsx` — SFW-styled home with two centered cards
- [ ] T029 [US1] Create `src/interfaces/nsfw/HomeView.tsx` — NSFW-styled home with two centered cards
- [ ] T030 [US1] Implement PDF card: PDF icon, "PDF" label, `onClick` → `navigate('/conversion')`, hover effect
- [ ] T031 [US1] Implement "Coming Soon" card: "+" icon, "Coming Soon" label, `opacity-50`, `cursor-not-allowed`, no `onClick`
- [ ] T032 [US1] Wire `App.tsx` to render `sfw/HomeView.tsx` or `nsfw/HomeView.tsx` based on mode context
- [ ] T033 [US1] Ensure TopBar is rendered above the home view content

**Checkpoint**: Home view renders correctly in both SFW and NSFW modes. PDF card navigates, Coming Soon card is inert.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Visual polish and edge case handling.

- [ ] T034 Ensure cards remain centered on window resize (flexbox/grid centering)
- [ ] T035 Add transition animation when navigating between views
- [ ] T036 Ensure SFW/NSFW toggle refreshes the home view immediately
- [ ] T037 Verify Electron window has reasonable minimum dimensions (800x600)
- [ ] T038 Add app title and icon in Electron's `BrowserWindow` config

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — creates entire frontend project from scratch.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS user story.
- **User Story 1 (Phase 3)**: Depends on Foundational. Single story — no sub-dependencies.
- **Polish (Phase 4)**: Depends on US1 completion.

### Within User Story 1

- Shared components (Card, icons) before view components
- SFW view before NSFW view (NSFW is a visual variant)
- Tests in parallel with implementation

## Notes

- The Home View is the simplest view. Its plan includes full project scaffolding because no frontend code exists yet. Later plans (Conversion, History, Settings) assume this skeleton is in place.
- Each view has separate SFW and NSFW implementations under `interfaces/sfw/` and `interfaces/nsfw/`. The mode context determines which to render. Both share the same props/behavior — only styling differs.
- `electron-store` is used for persisted settings (mode preference, default options). For the MVP, `localStorage` can serve as fallback during development outside Electron.
