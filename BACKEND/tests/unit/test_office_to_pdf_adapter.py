from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from adapters.output.converters.office_to_pdf_adapter import OfficeToPdfAdapter
from domain.entities import ConversionError, FileFormat


class TestOfficeToPdfAdapter:
    def test_supports_docx_to_pdf(self, settings):
        adapter = OfficeToPdfAdapter(settings)
        assert adapter.supports(FileFormat.DOCX, FileFormat.PDF) is True

    def test_supports_xlsx_to_pdf(self, settings):
        adapter = OfficeToPdfAdapter(settings)
        assert adapter.supports(FileFormat.XLSX, FileFormat.PDF) is True

    def test_supports_pptx_to_pdf(self, settings):
        adapter = OfficeToPdfAdapter(settings)
        assert adapter.supports(FileFormat.PPTX, FileFormat.PDF) is True

    def test_does_not_support_pdf_to_docx(self, settings):
        adapter = OfficeToPdfAdapter(settings)
        assert adapter.supports(FileFormat.PDF, FileFormat.DOCX) is False

    @patch("adapters.output.converters.office_to_pdf_adapter.subprocess.run")
    def test_convert_calls_libreoffice(self, mock_run, settings, tmp_path):
        adapter = OfficeToPdfAdapter(settings)
        adapter._soffice_path = "/fake/soffice"

        source = tmp_path / "test.docx"
        source.write_text("fake docx")
        target = tmp_path / "output.pdf"

        def _fake_run(*args, **kwargs):
            cmd_args = args[0]
            outdir_idx = cmd_args.index("--outdir")
            output_dir = Path(cmd_args[outdir_idx + 1])
            pdf_file = output_dir / "test.pdf"
            pdf_file.write_text("fake pdf content")
            return MagicMock(returncode=0)

        mock_run.side_effect = _fake_run

        adapter.convert(source, target, {})

        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        assert "--headless" in cmd_args
        assert "--convert-to" in cmd_args
        assert "pdf" in cmd_args

        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        assert "--headless" in cmd_args
        assert "--convert-to" in cmd_args
        assert "pdf" in cmd_args

    @patch("adapters.output.converters.office_to_pdf_adapter.subprocess.run")
    def test_convert_handles_nonzero_exit_code(self, mock_run, settings, tmp_path):
        mock_result = MagicMock(returncode=1, stderr="Some error")
        mock_run.return_value = mock_result

        adapter = OfficeToPdfAdapter(settings)
        adapter._soffice_path = "/fake/soffice"

        source = tmp_path / "test.docx"
        source.write_text("fake docx")
        target = tmp_path / "output.pdf"

        with pytest.raises(ConversionError, match="LibreOffice conversion failed"):
            adapter.convert(source, target, {})

    @patch("adapters.output.converters.office_to_pdf_adapter.subprocess.run")
    def test_convert_handles_password_protected(self, mock_run, settings, tmp_path):
        mock_result = MagicMock(returncode=1, stderr="password required")
        mock_run.return_value = mock_result

        adapter = OfficeToPdfAdapter(settings)
        adapter._soffice_path = "/fake/soffice"

        source = tmp_path / "test.docx"
        source.write_text("fake docx")
        target = tmp_path / "output.pdf"

        with pytest.raises(ConversionError, match="password-protected"):
            adapter.convert(source, target, {})

    def test_convert_without_libreoffice_raises_error(self, settings, tmp_path):
        adapter = OfficeToPdfAdapter(settings)
        adapter._soffice_path = None

        source = tmp_path / "test.docx"
        source.write_text("fake docx")
        target = tmp_path / "output.pdf"

        with pytest.raises(ConversionError, match="LibreOffice is not installed"):
            adapter.convert(source, target, {})
