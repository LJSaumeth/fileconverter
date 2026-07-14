import platform
import shutil
import subprocess
from pathlib import Path

from domain.entities import ConversionError, FileFormat
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import Settings


class OfficeToPdfAdapter(FileConverterPort):
    SUPPORTED_SOURCES = {FileFormat.DOCX, FileFormat.XLSX, FileFormat.PPTX}

    def __init__(self, settings: Settings):
        self._settings = settings
        self._soffice_path = self._find_libreoffice()

    def supports(self, source: FileFormat, target: FileFormat) -> bool:
        return source in self.SUPPORTED_SOURCES and target == FileFormat.PDF

    def convert(self, source_path: Path, target_path: Path, options: dict) -> None:
        if self._soffice_path is None:
            raise ConversionError(self._missing_libreoffice_message())

        output_dir = target_path.parent / f"_lo_{target_path.stem}"
        output_dir.mkdir(parents=True, exist_ok=True)

        timeout = self._settings.office_to_pdf_timeout_seconds
        cmd = [
            self._soffice_path,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(source_path),
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired as e:
            shutil.rmtree(output_dir, ignore_errors=True)
            raise ConversionError(
                f"Conversion timed out after {timeout} seconds. "
                "The document may be too large or complex."
            ) from e
        except FileNotFoundError as e:
            shutil.rmtree(output_dir, ignore_errors=True)
            raise ConversionError(self._missing_libreoffice_message()) from e

        if result.returncode != 0:
            stderr = result.stderr or ""
            shutil.rmtree(output_dir, ignore_errors=True)

            if "password" in stderr.lower():
                raise ConversionError(
                    "This document is password-protected and cannot be converted"
                )
            raise ConversionError(
                f"LibreOffice conversion failed: {stderr.strip() or 'Unknown error'}"
            )

        generated = list(output_dir.glob("*.pdf"))
        if not generated:
            shutil.rmtree(output_dir, ignore_errors=True)
            raise ConversionError("LibreOffice did not produce an output file")

        output_pdf = generated[0]
        shutil.move(str(output_pdf), str(target_path))
        shutil.rmtree(output_dir, ignore_errors=True)

    def _find_libreoffice(self) -> str | None:
        explicit = self._settings.libreoffice_path
        if explicit and Path(explicit).exists():
            return explicit

        system = platform.system()
        if system == "Windows":
            candidates = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
            for c in candidates:
                if Path(c).exists():
                    return c
            found = shutil.which("soffice.exe") or shutil.which("soffice")
            return found

        if system == "Darwin":
            candidates = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            ]
            for c in candidates:
                if Path(c).exists():
                    return c
            return shutil.which("soffice") or shutil.which("libreoffice")

        return shutil.which("libreoffice") or shutil.which("soffice")

    def _missing_libreoffice_message(self) -> str:
        system = platform.system()
        if system == "Windows":
            return (
                "LibreOffice is not installed. Please install it from "
                "https://www.libreoffice.org/download/ and restart the application."
            )
        if system == "Darwin":
            return (
                "LibreOffice is not installed. Please install it from "
                "https://www.libreoffice.org/download/ and restart the application."
            )
        return (
            "LibreOffice is not installed. Install it via your package manager "
            "(e.g. 'sudo apt install libreoffice') and restart the application."
        )
