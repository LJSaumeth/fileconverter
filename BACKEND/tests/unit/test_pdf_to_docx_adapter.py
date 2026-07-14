import pytest

from adapters.output.converters.pdf_to_docx_adapter import PdfToDocxAdapter
from adapters.output.converters.pdf_to_docx_ocr_adapter import PdfToDocxOcrAdapter
from domain.entities import ConversionError, FileFormat


class TestPdfToDocxAdapter:
    def test_supports_pdf_to_docx(self, settings):
        adapter = PdfToDocxAdapter(settings)
        assert adapter.supports(FileFormat.PDF, FileFormat.DOCX) is True

    def test_does_not_support_png_to_docx(self, settings):
        adapter = PdfToDocxAdapter(settings)
        assert adapter.supports(FileFormat.PNG, FileFormat.DOCX) is False

    def test_convert_requires_pdf2docx(self, settings, tmp_path):
        adapter = PdfToDocxAdapter(settings)
        source = tmp_path / "test.pdf"
        source.write_bytes(b"%PDF-1.4 dummy")
        target = tmp_path / "output.docx"

        import importlib.util

        if importlib.util.find_spec("pdf2docx") is None:
            with pytest.raises(ConversionError, match="pdf2docx is not installed"):
                adapter.convert(source, target, {})


class TestPdfToDocxOcrAdapter:
    def test_supports_pdf_to_docx(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        assert adapter.supports(FileFormat.PDF, FileFormat.DOCX) is True

    def test_convert_raises_not_implemented(self, settings, tmp_path):
        adapter = PdfToDocxOcrAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.docx"

        with pytest.raises(NotImplementedError):
            adapter.convert(source, target, {})
