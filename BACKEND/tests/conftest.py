from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from domain.entities import ConversionJob, FileFormat
from domain.ports.output.converter_registry_port import ConverterRegistryPort
from domain.ports.output.file_converter_port import FileConverterPort
from domain.ports.output.file_storage_port import FileStoragePort
from infrastructure.config import Settings

# ── Fixtures for all test suites ─────────────────────────────────────


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def sample_pdf_job(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy")
    return ConversionJob(
        job_id=uuid4(),
        source_path=pdf_path,
        source_format=FileFormat.PDF,
        target_format=FileFormat.PNG,
        options={"dpi": 150},
    )


@pytest.fixture
def sample_image_job(tmp_path):
    img_path = tmp_path / "sample.png"
    img_path.write_bytes(b"fake png content")
    return ConversionJob(
        job_id=uuid4(),
        source_path=img_path,
        source_format=FileFormat.PNG,
        target_format=FileFormat.PDF,
        options={},
    )


# ── Mock ports ───────────────────────────────────────────────────────


@pytest.fixture
def mock_converter() -> FileConverterPort:
    converter = MagicMock(spec=FileConverterPort)
    converter.supports.return_value = True
    converter.convert.return_value = None
    return converter


@pytest.fixture
def mock_registry(mock_converter) -> ConverterRegistryPort:
    registry = MagicMock(spec=ConverterRegistryPort)
    registry.get_converter.return_value = mock_converter
    return registry


@pytest.fixture
def mock_storage() -> FileStoragePort:
    storage = MagicMock(spec=FileStoragePort)
    storage.save_temp_file.return_value = MagicMock()
    storage.get_output_path.return_value = MagicMock()
    storage.cleanup.return_value = None
    return storage


@pytest.fixture
def mock_progress_notifier():
    notifier = MagicMock()
    notifier.notify = AsyncMock()
    return notifier
