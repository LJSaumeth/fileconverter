from unittest.mock import MagicMock
from uuid import uuid4

from application.use_cases.convert_file import ConvertFileService
from application.use_cases.list_supported_conversions import (
    ListSupportedConversionsService,
)
from domain.entities import (
    ConversionError,
    ConversionJob,
    ConversionStatus,
    FileFormat,
)


class TestConvertFileService:
    """Tests for ConvertFileService — the core orchestration use case."""

    async def test_successful_conversion(self, mock_registry, mock_storage):
        service = ConvertFileService(mock_registry, mock_storage)

        job = ConversionJob(
            job_id=uuid4(),
            source_path=magic_path(),
            source_format=FileFormat.PDF,
            target_format=FileFormat.PNG,
        )
        result = await service.execute(job)

        assert result.status == ConversionStatus.COMPLETED
        assert result.error_message is None
        mock_registry.get_converter.assert_called_once_with(FileFormat.PDF, FileFormat.PNG)
        mock_storage.get_output_path.assert_called_once()

    async def test_conversion_failure_propagates(self, mock_registry, mock_storage):
        converter = mock_registry.get_converter.return_value
        converter.convert.side_effect = ConversionError("Render failed")

        service = ConvertFileService(mock_registry, mock_storage)
        job = ConversionJob(
            job_id=uuid4(),
            source_path=magic_path(),
            source_format=FileFormat.PDF,
            target_format=FileFormat.PNG,
        )

        result = await service.execute(job)

        assert result.status == ConversionStatus.FAILED
        assert "Render failed" in (result.error_message or "")
        mock_storage.cleanup.assert_called_once()

    async def test_unsupported_conversion(self, mock_registry, mock_storage):
        mock_registry.get_converter.side_effect = ConversionError("not supported")

        service = ConvertFileService(mock_registry, mock_storage)
        job = ConversionJob(
            job_id=uuid4(),
            source_path=magic_path(),
            source_format=FileFormat.PDF,
            target_format=FileFormat.DOCX,
        )

        result = await service.execute(job)

        assert result.status == ConversionStatus.FAILED
        assert "not supported" in (result.error_message or "").lower()

    async def test_progress_notifier_invoked_on_success(
        self, mock_registry, mock_storage, mock_progress_notifier
    ):
        service = ConvertFileService(mock_registry, mock_storage)
        job = ConversionJob(
            job_id=uuid4(),
            source_path=magic_path(),
            source_format=FileFormat.PDF,
            target_format=FileFormat.PNG,
        )

        result = await service.execute(job, progress_notifier=mock_progress_notifier)

        assert result.status == ConversionStatus.COMPLETED
        # Should have been called at least twice (0% and 100%)
        assert mock_progress_notifier.notify.call_count >= 2

    async def test_progress_notifier_invoked_on_failure(
        self, mock_registry, mock_storage, mock_progress_notifier
    ):
        converter = mock_registry.get_converter.return_value
        converter.convert.side_effect = ConversionError("fail")

        service = ConvertFileService(mock_registry, mock_storage)
        job = ConversionJob(
            job_id=uuid4(),
            source_path=magic_path(),
            source_format=FileFormat.PDF,
            target_format=FileFormat.PNG,
        )

        result = await service.execute(job, progress_notifier=mock_progress_notifier)

        assert result.status == ConversionStatus.FAILED
        # Should have been called at least once (0% or 100% with FAILED)
        assert mock_progress_notifier.notify.call_count >= 1


class TestListSupportedConversionsService:
    """Tests for listing available conversion paths from registered converters."""

    def test_empty_converters(self):
        service = ListSupportedConversionsService([])
        result = service.execute()
        assert result == {}

    def test_single_converter(self, settings):
        from adapters.output.converters.pdf_to_image_adapter import PdfToImageAdapter

        adapter = PdfToImageAdapter(settings)
        service = ListSupportedConversionsService([adapter])
        result = service.execute()

        assert FileFormat.PDF in result
        assert FileFormat.PNG in result[FileFormat.PDF]
        assert FileFormat.JPG in result[FileFormat.PDF]

    def test_multiple_converters(self, settings):
        from adapters.output.converters.image_to_pdf_adapter import ImageToPdfAdapter
        from adapters.output.converters.pdf_to_image_adapter import PdfToImageAdapter

        converters = [
            PdfToImageAdapter(settings),
            ImageToPdfAdapter(settings),
        ]
        service = ListSupportedConversionsService(converters)
        result = service.execute()

        # PDF → PNG/JPG
        assert FileFormat.PNG in result.get(FileFormat.PDF, [])
        assert FileFormat.JPG in result.get(FileFormat.PDF, [])

        # PNG/JPG → PDF
        assert FileFormat.PDF in result.get(FileFormat.PNG, [])
        assert FileFormat.PDF in result.get(FileFormat.JPG, [])


# ── Helpers ──────────────────────────────────────────────────────────


def magic_path():
    p = MagicMock()
    p.__fspath__ = MagicMock(return_value="/tmp/test.pdf")
    return p
