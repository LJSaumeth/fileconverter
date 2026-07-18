# AGENTS.md

## Project status

- **Backend**: implemented — domain, application, adapters, infrastructure, tests (38 passing).
- **Frontend**: specs and plans exist, no code yet. Do not try to build or run frontend.

## Architecture (from README.md)

- **Desktop app** for local file conversion (PDF ↔ Word, Excel, PowerPoint, images).
- **Frontend**: React 18+ / Vite / TailwindCSS wrapped in Electron (not yet built).
- **Backend**: Python, **Hexagonal Architecture (Ports & Adapters)**. FastAPI + Uvicorn for HTTP/WebSocket input; PyMuPDF, LibreOffice headless, Pillow, pdf2docx, reportlab as output adapters.
- **Communication**: Electron spawns the backend as a child process, finds a free port via `get-port`, frontend talks HTTP/WebSocket to it (not yet wired).
- **Two UI modes** toggled by a switch and persisted: Basic/SFW (work-appropriate appearance) and NSFW (not work-appropriate appearance). Both modes share identical features (queue, history, advanced options); only the visual presentation differs.

## Dev commands

All commands run from `backend/`:

```
python -m pytest tests/ -v                # run all tests
python -m pytest tests/unit/test_pdf_to_image_adapter.py -v   # run one test file
python -m ruff check .                    # lint
python -m ruff check --fix .              # lint + auto-fix
python -m mypy .                          # typecheck
```

## Key design rule

**Adding a new conversion type must not require touching the domain or use-case layer.** Create a new adapter in `backend/adapters/output/converters/` that implements `FileConverterPort`, then register it in `backend/infrastructure/main.py:_create_converters()`. The port contracts are defined in README.md — treat them as the source of truth.

## System dependency: LibreOffice

The `office_to_pdf_adapter.py` (docx/xlsx/pptx → PDF) requires LibreOffice installed on the host. The adapter auto-detects it at:
- Windows: `C:\Program Files\LibreOffice\program\soffice.exe`
- macOS: `/Applications/LibreOffice.app/Contents/MacOS/soffice`
- Linux: `libreoffice` on PATH

If missing, the adapter raises a `ConversionError` with install instructions. Unit tests mock `subprocess.run` and don't need LibreOffice.

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

**Backend feature list:**
- pdf-to-image (PyMuPDF)
- image-to-pdf (Pillow + reportlab)
- docx-to-pdf (LibreOffice headless)
- pdf-to-docx (pdf2docx)

## Documentation workflow

- **Specs** go in `DOCS/{BACKEND,FRONTEND}/SPECS/` using the spec template. Specs require prioritized user stories (P1–Pn) with Gherkin-style acceptance scenarios, functional requirements (FR-XXX), and measurable success criteria.
- **Plans** go in `DOCS/{BACKEND,FRONTEND}/PLANS/` using the plan template. Plans follow phased execution: Setup → Foundational → User Stories (by priority) → Polish. Each story must be independently testable.
- Templates live at `DOCS/{BACKEND,FRONTEND}/{SPECS,PLANS}/` — follow their structure exactly.

## Code style

All code (Python and JavaScript/TypeScript) must follow **Clean Code** guidelines. Keep functions small, names meaningful, and modules focused on a single responsibility.

**Python**: pytest, coverage, ruff, mypy — all configured in `backend/pyproject.toml`.
**Frontend**: Vitest or Jest (not yet configured).
**Backend packaging**: PyInstaller for standalone executable (not yet wired).
**Desktop packaging**: electron-builder (not yet wired).
