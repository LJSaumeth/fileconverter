from uuid import uuid4

import pytest

from domain.entities import ConversionJob, FileFormat
from infrastructure.config import Settings


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
