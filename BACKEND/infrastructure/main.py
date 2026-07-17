import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.input.http.conversion_router import router as http_router
from adapters.input.websocket.connection_manager import ConnectionManager
from adapters.input.websocket.ws_router import router as ws_router
from adapters.output.storage.local_file_storage_adapter import LocalFileStorageAdapter
from application.use_cases.convert_file import ConvertFileService
from application.use_cases.list_supported_conversions import (
    ListSupportedConversionsService,
)
from domain.entities import FileFormat, UnsupportedConversionError
from domain.ports.output.converter_registry_port import ConverterRegistryPort
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import settings

# ── Logging ──────────────────────────────────────────────────────────

try:
    from loguru import logger

    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
except ImportError:
    import logging

    logger = logging.getLogger("fileconverter")
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    )


# ── Converter Registry (concrete wiring) ────────────────────────────


class ConverterRegistry(ConverterRegistryPort):
    def __init__(self, converters: list[FileConverterPort]) -> None:
        self._converters = converters

    def get_converter(self, source: FileFormat, target: FileFormat) -> FileConverterPort:
        for converter in self._converters:
            if converter.supports(source, target):
                return converter
        raise UnsupportedConversionError(
            f"No converter found for {source.value} -> {target.value}"
        )


def _create_converters() -> list[FileConverterPort]:
    converters: list[FileConverterPort] = []

    try:
        from adapters.output.converters.pdf_to_image_adapter import PdfToImageAdapter

        converters.append(PdfToImageAdapter(settings))
        logger.debug("Registered PdfToImageAdapter")
    except ImportError:
        logger.warning("PdfToImageAdapter not available (PyMuPDF missing?)")

    try:
        from adapters.output.converters.image_to_pdf_adapter import ImageToPdfAdapter

        converters.append(ImageToPdfAdapter(settings))
        logger.debug("Registered ImageToPdfAdapter")
    except ImportError:
        logger.warning("ImageToPdfAdapter not available (Pillow / reportlab missing?)")

    try:
        from adapters.output.converters.office_to_pdf_adapter import OfficeToPdfAdapter

        converters.append(OfficeToPdfAdapter(settings))
        logger.debug("Registered OfficeToPdfAdapter")
    except ImportError:
        logger.warning("OfficeToPdfAdapter not available")

    try:
        from adapters.output.converters.pdf_to_docx_adapter import PdfToDocxAdapter

        converters.append(PdfToDocxAdapter(settings))
        logger.debug("Registered PdfToDocxAdapter")
    except ImportError:
        logger.warning("PdfToDocxAdapter not available (pdf2docx missing?)")

    try:
        from adapters.output.converters.pdf_to_docx_ocr_adapter import (
            PdfToDocxOcrAdapter,
        )

        converters.append(PdfToDocxOcrAdapter(settings))
        logger.debug("Registered PdfToDocxOcrAdapter")
    except ImportError:
        logger.warning(
            "PdfToDocxOcrAdapter not available (pytesseract / python-docx missing?)"
        )

    logger.info(
        "Registered {} converter(s).",
        len(converters),
    )
    return converters


# ── App factory ──────────────────────────────────────────────────────


def _parse_cors_origins(raw: str) -> list[str]:
    """Parse ``cors_origins`` — supports ``"*"`` and comma-separated URLs."""
    raw_stripped = raw.strip()
    if raw_stripped == "*" or "," not in raw_stripped:
        return [raw_stripped]
    return [origin.strip() for origin in raw_stripped.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and graceful shutdown."""
    logger.info("FileConverter backend starting…")
    logger.info(
        "Listen on {}:{} | CORS origins: {} | Max file size: {} MB",
        settings.host,
        settings.port if settings.port else "random",
        settings.cors_origins,
        settings.max_file_size_mb,
    )
    yield
    # ── Graceful shutdown: clean up temp files ───────────────────
    logger.info("Shutting down — cleaning up temporary files…")
    storage: LocalFileStorageAdapter | None = getattr(app.state, "file_storage", None)
    if storage is not None:
        try:
            import shutil

            temp_dir = storage._temp_dir  # type: ignore[union-attr]
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("Temporary directory removed: {}", temp_dir)
        except Exception as exc:
            logger.warning("Could not clean up temporary files: {}", exc)
    logger.info("FileConverter backend stopped.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FileConverter Backend",
        version="0.2.0",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────
    origins = _parse_cors_origins(settings.cors_origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Wiring (dependency injection) ────────────────────────────
    _wiring(app)

    # ── Routers ──────────────────────────────────────────────────
    app.include_router(http_router)
    app.include_router(ws_router)

    return app


def _wiring(app: FastAPI) -> None:
    file_storage = LocalFileStorageAdapter(settings.temp_dir)
    ws_manager = ConnectionManager()
    converters = _create_converters()
    converter_registry = ConverterRegistry(converters)

    convert_use_case = ConvertFileService(converter_registry, file_storage)
    list_use_case = ListSupportedConversionsService(converters)

    app.state.convert_use_case = convert_use_case
    app.state.list_use_case = list_use_case
    app.state.file_storage = file_storage
    app.state.ws_manager = ws_manager


# ── CLI entry point ──────────────────────────────────────────────────


def main() -> None:
    """Entry point for ``python -m infrastructure.main`` or PyInstaller binary."""
    uvicorn.run(
        "infrastructure.main:create_app",
        host=settings.host,
        port=settings.port,
        factory=True,
        reload=False,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
