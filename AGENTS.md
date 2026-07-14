# AGENTS.md

## Project status

This repo is **pre-implementation**. No code, dependency manifests, build configs, or dev tooling exist yet. Do not try to run, build, or test anything.

## Architecture (from README.md)

- **Desktop app** for local file conversion (PDF ↔ Word, Excel, PowerPoint, images).
- **Frontend**: React 18+ / Vite / TailwindCSS wrapped in Electron.
- **Backend**: Python, **Hexagonal Architecture (Ports & Adapters)**. FastAPI + Uvicorn for HTTP/WebSocket input; PyMuPDF, LibreOffice headless, Pillow, pdf2docx, reportlab as output adapters.
- **Communication**: Electron spawns the backend as a child process, finds a free port via `get-port`, frontend talks HTTP/WebSocket to it.
- **Two UI modes** toggled by a switch and persisted: Basic/SFW (work-appropriate appearance) and NSFW (not work-appropriate appearance). Both modes share identical features (queue, history, advanced options); only the visual presentation differs.

## Key design rule

**Adding a new conversion type must not require touching the domain or use-case layer.** Create a new adapter in `backend/adapters/output/converters/` that implements `FileConverterPort`, then register it in the wiring (`infrastructure/main.py`). The port contracts are defined in README.md — treat them as the source of truth.

## Documentation workflow

- **Specs** go in `DOCS/{BACKEND,FRONTEND}/SPECS/` using the spec template. Specs require prioritized user stories (P1–Pn) with Gherkin-style acceptance scenarios, functional requirements (FR-XXX), and measurable success criteria.
- **Plans** go in `DOCS/{BACKEND,FRONTEND}/PLANS/` using the plan template. Plans follow phased execution: Setup → Foundational → User Stories (by priority) → Polish. Each story must be independently testable.
- Templates live at `DOCS/{BACKEND,FRONTEND}/{SPECS,PLANS}/` — follow their structure exactly.

## Development workflow

**Backend first, frontend second.** Complete all backend phases before starting frontend work.

**Rule: 1 feature = 1 spec = 1 plan.** Each backend feature (e.g. pdf-to-image) gets its own spec file and its own plan file in `DOCS/BACKEND/`. Same for each frontend view.

**Phased execution order:**

1. **BACKEND: Specs** — create one spec per feature in `DOCS/BACKEND/SPECS/`
2. **BACKEND: Plans** — create one plan per feature in `DOCS/BACKEND/PLANS/`, derived from its spec
3. **BACKEND: Implementation** — implement each feature following its spec and plan
4. **FRONTEND: Specs** — create one spec per view in `DOCS/FRONTEND/SPECS/`
5. **FRONTEND: Plans** — create one plan per view in `DOCS/FRONTEND/PLANS/`, derived from its spec
6. **FRONTEND: Implementation** — implement each view following its spec and plan

**Backend feature list (as of now):**
- pdf-to-image
- image-to-pdf
- docx-to-pdf
- pdf-to-docx

## Code style

All code (Python and JavaScript/TypeScript) must follow **Clean Code** guidelines. Keep functions small, names meaningful, and modules focused on a single responsibility.

- **Python**: pytest, coverage, ruff, mypy (not yet configured)
- **Frontend**: Vitest or Jest (not yet configured)
- **Backend packaging**: PyInstaller for standalone executable
- **Desktop packaging**: electron-builder
