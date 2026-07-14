from pathlib import Path

from domain.entities import ConversionError, FileFormat
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import Settings


class PdfToDocxAdapter(FileConverterPort):
    def __init__(self, settings: Settings):
        self._settings = settings

    def supports(self, source: FileFormat, target: FileFormat) -> bool:
        return source == FileFormat.PDF and target == FileFormat.DOCX

    def convert(self, source_path: Path, target_path: Path, options: dict) -> None:
        try:
            from pdf2docx import Converter
        except ImportError as e:
            raise ConversionError(
                "pdf2docx is not installed. Run: pip install pdf2docx"
            ) from e

        try:
            cv = Converter(str(source_path))
        except Exception as e:
            raise ConversionError(f"Could not open PDF: {e}") from e

        try:
            cv.convert(str(target_path), start=0, end=None)
            cv.close()
        except Exception as e:
            cv.close()
            if "password" in str(e).lower():
                raise ConversionError(
                    "This PDF is password-protected and cannot be converted"
                ) from e
            raise ConversionError(f"PDF to DOCX conversion failed: {e}") from e
