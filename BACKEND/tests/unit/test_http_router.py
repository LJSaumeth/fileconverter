import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from adapters.input.http.conversion_router import router
from adapters.input.websocket.connection_manager import ConnectionManager
from application.use_cases.convert_file import ConvertFileService
from application.use_cases.list_supported_conversions import (
    ListSupportedConversionsService,
)
from domain.entities import ConversionResult, ConversionStatus, FileFormat


@pytest.fixture
def app(mock_registry, mock_storage):
    """Build a minimal FastAPI app with the conversion router wired."""
    app = FastAPI()
    app.state.convert_use_case = ConvertFileService(mock_registry, mock_storage)
    app.state.list_use_case = ListSupportedConversionsService([])
    app.state.file_storage = mock_storage
    app.state.ws_manager = ConnectionManager()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_method_not_allowed(self, client):
        response = client.post("/api/health")
        assert response.status_code == 405


class TestConvertEndpoint:
    def test_convert_success(self, app, client, tmp_path):
        output_file = tmp_path / "output.png"
        output_file.write_bytes(b"fake png data")

        async_mock = AsyncMock()
        async_mock.execute.return_value = ConversionResult(
            job_id=uuid4(),
            status=ConversionStatus.COMPLETED,
            output_path=output_file,
        )
        app.state.convert_use_case = async_mock

        response = client.post(
            "/api/convert",
            data={
                "source_format": "pdf",
                "target_format": "png",
                "options": json.dumps({"dpi": 300}),
            },
            files={"file": ("test.pdf", b"%PDF-1.4 test content", "application/pdf")},
        )

        assert response.status_code == 200

    def test_convert_unsupported_format(self, client):
        response = client.post(
            "/api/convert",
            data={
                "source_format": "pdf",
                "target_format": "exe",
                "options": "{}",
            },
            files={"file": ("test.pdf", b"content", "application/pdf")},
        )
        assert response.status_code == 400
        assert "Unsupported format" in response.text

    def test_convert_result_failed(self, app, client):
        async_mock = AsyncMock()
        async_mock.execute.return_value = ConversionResult(
            job_id=uuid4(),
            status=ConversionStatus.FAILED,
            output_path=None,
            error_message="Conversion error",
        )
        app.state.convert_use_case = async_mock

        response = client.post(
            "/api/convert",
            data={
                "source_format": "pdf",
                "target_format": "docx",
                "options": "{}",
            },
            files={"file": ("test.pdf", b"content", "application/pdf")},
        )
        assert response.status_code == 422
        assert "Conversion error" in response.text

    def test_convert_invalid_json_options(self, app, client, tmp_path):
        output_file = tmp_path / "output.png"
        output_file.write_bytes(b"fake png data")

        async_mock = AsyncMock()
        async_mock.execute.return_value = ConversionResult(
            job_id=uuid4(),
            status=ConversionStatus.COMPLETED,
            output_path=output_file,
        )
        app.state.convert_use_case = async_mock

        response = client.post(
            "/api/convert",
            data={
                "source_format": "pdf",
                "target_format": "png",
                "options": "not-json",
            },
            files={"file": ("test.pdf", b"content", "application/pdf")},
        )
        # Invalid JSON should fall back to empty dict and still work
        assert response.status_code == 200

    def test_convert_with_websocket_id_no_connection(self, client):
        response = client.post(
            "/api/convert",
            data={
                "source_format": "pdf",
                "target_format": "png",
                "options": "{}",
                "websocket_id": "nonexistent",
            },
            files={"file": ("test.pdf", b"content", "application/pdf")},
        )
        assert response.status_code == 400
        assert "No active WebSocket" in response.text


class TestConversionsEndpoint:
    def test_list_conversions(self, app, client):
        app.state.list_use_case.execute = MagicMock()
        app.state.list_use_case.execute.return_value = {
            FileFormat.PDF: [FileFormat.PNG, FileFormat.JPG],
        }

        response = client.get("/api/conversions")
        assert response.status_code == 200
        data = response.json()
        assert "pdf" in data
        assert "png" in data["pdf"]
        assert "jpg" in data["pdf"]
