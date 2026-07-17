from pathlib import Path
from uuid import UUID, uuid4

import pytest

from domain.entities import (
    ConversionError,
    ConversionJob,
    ConversionProgress,
    ConversionResult,
    ConversionStatus,
    FileFormat,
    UnsupportedConversionError,
)


class TestFileFormat:
    def test_str_enum_values(self):
        assert FileFormat.PDF.value == "pdf"
        assert FileFormat.DOCX.value == "docx"
        assert FileFormat.PNG.value == "png"
        assert FileFormat.JPG.value == "jpg"

    def test_from_string(self):
        assert FileFormat("pdf") == FileFormat.PDF
        assert FileFormat("docx") == FileFormat.DOCX

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            FileFormat("exe")


class TestConversionStatus:
    def test_enum_values(self):
        assert ConversionStatus.PENDING.value == "pending"
        assert ConversionStatus.IN_PROGRESS.value == "in_progress"
        assert ConversionStatus.COMPLETED.value == "completed"
        assert ConversionStatus.FAILED.value == "failed"


class TestConversionJob:
    def test_minimal_job(self):
        job_id = uuid4()
        job = ConversionJob(
            job_id=job_id,
            source_path=Path("/tmp/test.pdf"),
            source_format=FileFormat.PDF,
            target_format=FileFormat.PNG,
            options={"dpi": 150},
        )
        assert isinstance(job.job_id, UUID)
        assert job.job_id == job_id
        assert job.source_format == FileFormat.PDF
        assert job.target_format == FileFormat.PNG
        assert job.options == {"dpi": 150}

    def test_default_options_empty_dict(self):
        job = ConversionJob(
            job_id=uuid4(),
            source_path=Path("/tmp/test.pdf"),
            source_format=FileFormat.PDF,
            target_format=FileFormat.DOCX,
        )
        assert job.options == {}

    def test_job_is_immutable(self):
        job = ConversionJob(
            job_id=uuid4(),
            source_path=Path("/tmp/test.pdf"),
            source_format=FileFormat.PDF,
            target_format=FileFormat.DOCX,
        )
        with pytest.raises(AttributeError):
            job.options = {"new": "value"}  # type: ignore[misc]

    def test_sample_pdf_job(self, sample_pdf_job):
        assert sample_pdf_job.source_path.exists()
        assert sample_pdf_job.source_path.read_bytes() == b"%PDF-1.4 dummy"


class TestConversionResult:
    def test_completed_result(self):
        result = ConversionResult(
            job_id=uuid4(),
            status=ConversionStatus.COMPLETED,
            output_path=Path("/tmp/output.pdf"),
        )
        assert result.status == ConversionStatus.COMPLETED
        assert result.output_path == Path("/tmp/output.pdf")
        assert result.error_message is None

    def test_failed_result(self):
        result = ConversionResult(
            job_id=uuid4(),
            status=ConversionStatus.FAILED,
            output_path=None,
            error_message="Something went wrong",
        )
        assert result.status == ConversionStatus.FAILED
        assert result.output_path is None
        assert result.error_message == "Something went wrong"


class TestConversionProgress:
    def test_minimal_progress(self):
        job_id = uuid4()
        progress = ConversionProgress(
            job_id=job_id,
            percentage=50,
            status=ConversionStatus.IN_PROGRESS,
        )
        assert progress.job_id == job_id
        assert progress.percentage == 50
        assert progress.message is None

    def test_progress_with_message(self):
        progress = ConversionProgress(
            job_id=uuid4(),
            percentage=100,
            status=ConversionStatus.COMPLETED,
            message="Done!",
        )
        assert progress.message == "Done!"


class TestExceptions:
    def test_conversion_error_default(self):
        error = ConversionError("error occurred")
        assert str(error) == "error occurred"
        assert error.job_id is None

    def test_conversion_error_with_job_id(self):
        job_id = uuid4()
        error = ConversionError("error", job_id=job_id)
        assert error.job_id == job_id

    def test_unsupported_conversion_error(self):
        error = UnsupportedConversionError("not supported", job_id=uuid4())
        assert isinstance(error, ConversionError)
        assert "not supported" in str(error)
