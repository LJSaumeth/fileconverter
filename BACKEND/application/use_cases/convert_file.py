from domain.entities import (
    ConversionError,
    ConversionJob,
    ConversionResult,
    ConversionStatus,
)
from domain.ports.input.convert_file_use_case import ConvertFileUseCase
from domain.ports.output.converter_registry_port import ConverterRegistryPort
from domain.ports.output.file_storage_port import FileStoragePort


class ConvertFileService(ConvertFileUseCase):
    def __init__(
        self,
        converter_registry: ConverterRegistryPort,
        file_storage: FileStoragePort,
    ):
        self._converter_registry = converter_registry
        self._file_storage = file_storage

    def execute(self, job: ConversionJob) -> ConversionResult:
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

        try:
            converter.convert(job.source_path, output_path, job.options)
        except ConversionError as e:
            self._file_storage.cleanup(job.job_id)
            return ConversionResult(
                job_id=job.job_id,
                status=ConversionStatus.FAILED,
                output_path=None,
                error_message=str(e),
            )

        return ConversionResult(
            job_id=job.job_id,
            status=ConversionStatus.COMPLETED,
            output_path=output_path,
        )
