import pytest

from adapters.output.converters.pdf_to_docx_adapter import PdfToDocxAdapter
from adapters.output.converters.pdf_to_docx_ocr_adapter import PdfToDocxOcrAdapter
from domain.entities import ConversionError, FileFormat


class TestPdfToDocxAdapter:
    """Tests for text-based PDF → DOCX converter (pdf2docx)."""

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
    """Tests for OCR-based PDF → DOCX converter (Tesseract)."""

    def test_supports_pdf_to_docx(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        assert adapter.supports(FileFormat.PDF, FileFormat.DOCX) is True

    def test_does_not_support_unsupported_source(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        assert adapter.supports(FileFormat.PNG, FileFormat.DOCX) is False

    def test_convert_checks_dependencies(self, settings, tmp_path):
        """Without Tesseract installed, the adapter should raise ConversionError."""
        adapter = PdfToDocxOcrAdapter(settings)
        source = tmp_path / "test.pdf"
        source.write_bytes(b"%PDF-1.4 dummy")
        target = tmp_path / "output.docx"

        # If tesseract isn't found, the adapter will raise
        if adapter._tesseract_cmd is None:
            with pytest.raises(
                ConversionError, match="Tesseract engine"
            ):
                adapter.convert(source, target, {})
        else:
            # Tesseract IS available — attempt real conversion
            # (may still fail on missing pytesseract/python-docx packages)
            try:
                adapter.convert(source, target, {})
            except ConversionError as e:
                assert any(
                    keyword in str(e).lower()
                    for keyword in [
                        "pytesseract",
                        "python-docx",
                        "not installed",
                        "missing",
                    ]
                )

    def test_resolve_page_indices_all_pages(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        assert adapter._resolve_page_indices(None, 5) == [0, 1, 2, 3, 4]

    def test_resolve_page_indices_range(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        assert adapter._resolve_page_indices((2, 4), 5) == [1, 2, 3]

    def test_resolve_page_indices_reversed_range(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        assert adapter._resolve_page_indices((4, 2), 5) == [1, 2, 3]

    def test_resolve_page_indices_out_of_range(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        with pytest.raises(ConversionError, match="outside the document"):
            adapter._resolve_page_indices((10, 20), 5)

    def test_resolve_page_indices_specific_list(self, settings):
        adapter = PdfToDocxOcrAdapter(settings)
        assert adapter._resolve_page_indices([1, 3, 5], 5) == [0, 2, 4]
