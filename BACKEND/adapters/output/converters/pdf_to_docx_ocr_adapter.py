from pathlib import Path

from domain.entities import FileFormat
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import Settings


class PdfToDocxOcrAdapter(FileConverterPort):
    """
    OCR-based PDF to DOCX adapter (deferred implementation).
    Intended to use Tesseract for text extraction from scanned/image-based PDFs.
    Currently raises NotImplementedError — structure exists per FR-007.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    def supports(self, source: FileFormat, target: FileFormat) -> bool:
        return source == FileFormat.PDF and target == FileFormat.DOCX

    def convert(self, source_path: Path, target_path: Path, options: dict) -> None:
        raise NotImplementedError(
            "OCR-based PDF to DOCX conversion is not yet implemented. "
            "This adapter is reserved for future Tesseract integration."
        )
