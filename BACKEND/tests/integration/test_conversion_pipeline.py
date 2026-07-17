"""Integration tests: end-to-end conversion pipeline.

These tests verify the full wiring — domain → application → adapters —
using real converter implementations where possible and the FastAPI
TestClient for HTTP-level assertions.

Fixtures imported from ``tests.conftest`` provide shared test state.
"""

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from adapters.input.http.conversion_router import router as http_router
from adapters.input.websocket.connection_manager import ConnectionManager
from adapters.output.storage.local_file_storage_adapter import (
    LocalFileStorageAdapter,
)
from application.use_cases.convert_file import ConvertFileService
from application.use_cases.list_supported_conversions import (
    ListSupportedConversionsService,
)
from domain.entities import (
    ConversionError,
    FileFormat,
)
from domain.ports.output.converter_registry_port import ConverterRegistryPort
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import Settings

# ── Inline ConverterRegistry (like main.py but lightweight) ──────────


class ConverterRegistry(ConverterRegistryPort):
    def __init__(self, converters: list[FileConverterPort]) -> None:
        self._converters = converters

    def get_converter(self, source: FileFormat, target: FileFormat) -> FileConverterPort:
        for converter in self._converters:
            if converter.supports(source, target):
                return converter
        raise ConversionError(f"No converter for {source.value} -> {target.value}")


# ── Fixtures ─────────────────────────────────────────────────────────


def _create_app(temp_dir) -> FastAPI:
    """Build the application with real adapters for integration testing."""
    settings = Settings()
    settings.temp_dir = temp_dir

    file_storage = LocalFileStorageAdapter(settings.temp_dir)

    converters: list[FileConverterPort] = []
    try:
        from adapters.output.converters.pdf_to_image_adapter import PdfToImageAdapter
        converters.append(PdfToImageAdapter(settings))
    except ImportError:
        pass

    try:
        from adapters.output.converters.image_to_pdf_adapter import ImageToPdfAdapter
        converters.append(ImageToPdfAdapter(settings))
    except ImportError:
        pass

    try:
        from adapters.output.converters.office_to_pdf_adapter import OfficeToPdfAdapter
        converters.append(OfficeToPdfAdapter(settings))
    except ImportError:
        pass

    try:
        from adapters.output.converters.pdf_to_docx_adapter import PdfToDocxAdapter
        converters.append(PdfToDocxAdapter(settings))
    except ImportError:
        pass

    registry = ConverterRegistry(converters)

    app = FastAPI()
    app.state.convert_use_case = ConvertFileService(registry, file_storage)
    app.state.list_use_case = ListSupportedConversionsService(converters)
    app.state.file_storage = file_storage
    app.state.ws_manager = ConnectionManager()

    app.include_router(http_router)
    return app


@pytest.fixture
def integration_app(tmp_path):
    return _create_app(tmp_path / "fc_integration")


@pytest.fixture
def client(integration_app):
    return TestClient(integration_app)


# ── Tests ────────────────────────────────────────────────────────────


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestListConversions:
    def test_returns_at_least_one_conversion(self, client):
        resp = client.get("/api/conversions")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        # With at least one converter registered we expect some entries
        if data:
            for _source, targets in data.items():
                assert isinstance(targets, list)
                assert len(targets) > 0


class TestPdfToImageConversion:
    """Requires PyMuPDF (fitz) to be installed."""

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("fitz"),
        reason="PyMuPDF not installed",
    )
    def test_convert_pdf_to_png(self, client, tmp_path):
        """Create a real 1-page PDF, POST it, verify PNG output."""
        import fitz

        pdf_path = tmp_path / "test.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Integration test")
        doc.save(str(pdf_path))
        doc.close()

        pdf_bytes = pdf_path.read_bytes()

        resp = client.post(
            "/api/convert",
            data={
                "source_format": "pdf",
                "target_format": "png",
                "options": json.dumps({"dpi": 150}),
            },
            files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
        )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


class TestImageToPdfConversion:
    """Requires Pillow to be installed."""

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("PIL"),
        reason="Pillow not installed",
    )
    def test_convert_png_to_pdf(self, client, tmp_path):
        from PIL import Image

        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(img_path)

        img_bytes = img_path.read_bytes()

        resp = client.post(
            "/api/convert",
            data={
                "source_format": "png",
                "target_format": "pdf",
                "options": json.dumps({}),
            },
            files={"file": ("test.png", img_bytes, "image/png")},
        )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


class TestUnsupportedConversion:
    def test_unsupported_format_returns_400(self, client):
        resp = client.post(
            "/api/convert",
            data={
                "source_format": "pdf",
                "target_format": "exe",
                "options": "{}",
            },
            files={"file": ("test.pdf", b"data", "application/pdf")},
        )
        assert resp.status_code == 400
