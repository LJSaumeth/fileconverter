import asyncio

from domain.entities import (
    ConversionError,
    ConversionJob,
    ConversionProgress,
    ConversionResult,
    ConversionStatus,
)
from domain.ports.input.convert_file_use_case import ConvertFileUseCase
from domain.ports.output.converter_registry_port import ConverterRegistryPort
from domain.ports.output.file_storage_port import FileStoragePort
from domain.ports.output.progress_notifier_port import ProgressNotifierPort


class ConvertFileService(ConvertFileUseCase):
    """Orchestrates a file conversion end-to-end.

    The conversion itself runs in a thread pool executor so the
    event loop is not blocked. If a ``progress_notifier`` is provided,
    progress updates are pushed before and after the conversion.
    """

    def __init__(
        self,
        converter_registry: ConverterRegistryPort,
        file_storage: FileStoragePort,
    ) -> None:
        self._converter_registry = converter_registry
        self._file_storage = file_storage

    async def execute(
        self,
        job: ConversionJob,
        progress_notifier: ProgressNotifierPort | None = None,
    ) -> ConversionResult:
        # ── Resolve converter ────────────────────────────────────
        try:
            converter = self._converter_registry.get_converter(
                job.source_format, job.target_format
            )
        except ConversionError:
            return ConversionResult(
                job_id=job.job_id,
                status=ConversionStatus.FAILED,
                output_path=None,
                error_message=(
                    f"Conversion from {job.source_format.value} to "
                    f"{job.target_format.value} is not supported"
                ),
            )

        output_path = self._file_storage.get_output_path(
            job.job_id, job.target_format.value
        )

        # ── Notify: started ──────────────────────────────────────
        if progress_notifier:
            await progress_notifier.notify(
                ConversionProgress(
                    job_id=job.job_id,
                    percentage=0,
                    status=ConversionStatus.IN_PROGRESS,
                    message="Starting conversion…",
                )
            )

        # ── Run conversion in thread pool ────────────────────────
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, converter.convert, job.source_path, output_path, job.options
            )
        except ConversionError as e:
            self._file_storage.cleanup(job.job_id)
            if progress_notifier:
                await progress_notifier.notify(
                    ConversionProgress(
                        job_id=job.job_id,
                        percentage=100,
                        status=ConversionStatus.FAILED,
                        message=str(e),
                    )
                )
            return ConversionResult(
                job_id=job.job_id,
                status=ConversionStatus.FAILED,
                output_path=None,
                error_message=str(e),
            )

        # ── Notify: completed ────────────────────────────────────
        if progress_notifier:
            await progress_notifier.notify(
                ConversionProgress(
                    job_id=job.job_id,
                    percentage=100,
                    status=ConversionStatus.COMPLETED,
                    message="Conversion complete.",
                )
            )

        return ConversionResult(
            job_id=job.job_id,
            status=ConversionStatus.COMPLETED,
            output_path=output_path,
        )
