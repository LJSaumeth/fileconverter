from pathlib import Path

import fitz
import pytest

from adapters.output.converters.pdf_to_image_adapter import PdfToImageAdapter
from domain.entities import ConversionError, FileFormat


class TestPdfToImageAdapter:
    def test_supports_pdf_to_png(self, settings):
        adapter = PdfToImageAdapter(settings)
        assert adapter.supports(FileFormat.PDF, FileFormat.PNG) is True

    def test_supports_pdf_to_jpg(self, settings):
        adapter = PdfToImageAdapter(settings)
        assert adapter.supports(FileFormat.PDF, FileFormat.JPG) is True

    def test_does_not_support_unsupported_target(self, settings):
        adapter = PdfToImageAdapter(settings)
        assert adapter.supports(FileFormat.PDF, FileFormat.DOCX) is False

    def test_does_not_support_non_pdf_source(self, settings):
        adapter = PdfToImageAdapter(settings)
        assert adapter.supports(FileFormat.PNG, FileFormat.JPG) is False

    def test_convert_single_page_pdf_to_png(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.png"
        _create_test_pdf(source, pages=1)

        adapter.convert(source, target, {})

        # Single page is saved directly to target_path (not suffixed)
        assert target.exists()
        assert target.stat().st_size > 0

    def test_convert_multi_page_pdf(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.png"
        _create_test_pdf(source, pages=3)

        adapter.convert(source, target, {})

        for i in range(3):
            p = tmp_path / f"output_page_{i + 1}.png"
            assert p.exists()
            assert p.stat().st_size > 0

    def test_convert_with_dpi(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.jpg"
        _create_test_pdf(source, pages=1)

        adapter.convert(source, target, {"dpi": 300})

        # Single page is saved directly to target_path
        assert target.exists()
        assert target.stat().st_size > 0

    def test_convert_six_or_more_pages_produces_zip(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.png"
        _create_test_pdf(source, pages=6)

        adapter.convert(source, target, {})

        zip_file = tmp_path / "output.png"
        assert zip_file.exists()
        assert zip_file.suffix == ".png"

        import zipfile

        with zipfile.ZipFile(zip_file, "r") as zf:
            names = zf.namelist()
            assert len(names) == 6

    def test_convert_five_or_less_pages_produces_individual_files(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.png"
        _create_test_pdf(source, pages=5)

        adapter.convert(source, target, {})

        for i in range(5):
            p = tmp_path / f"output_page_{i + 1}.png"
            assert p.exists()

    def test_page_range_selection(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.png"
        _create_test_pdf(source, pages=5)

        adapter.convert(source, target, {"pages": (2, 4)})

        assert not (tmp_path / "output_page_1.png").exists()
        assert (tmp_path / "output_page_2.png").exists()
        assert (tmp_path / "output_page_3.png").exists()
        assert (tmp_path / "output_page_4.png").exists()
        assert not (tmp_path / "output_page_5.png").exists()

    def test_reversed_page_range_is_normalized(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.png"
        _create_test_pdf(source, pages=5)

        adapter.convert(source, target, {"pages": (4, 2)})

        assert not (tmp_path / "output_page_1.png").exists()
        assert (tmp_path / "output_page_2.png").exists()
        assert (tmp_path / "output_page_3.png").exists()
        assert (tmp_path / "output_page_4.png").exists()

    def test_out_of_range_page_raises_error(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.png"
        _create_test_pdf(source, pages=3)

        with pytest.raises(ConversionError, match="outside the document"):
            adapter.convert(source, target, {"pages": (5, 8)})

    def test_corrupted_pdf_raises_error(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "invalid.pdf"
        source.write_text("not a pdf")
        target = tmp_path / "output.png"

        with pytest.raises(ConversionError, match="Could not open PDF"):
            adapter.convert(source, target, {})

    def test_jpg_output_with_quality(self, settings, tmp_path):
        adapter = PdfToImageAdapter(settings)
        source = tmp_path / "test.pdf"
        target = tmp_path / "output.jpg"
        _create_test_pdf(source, pages=1)

        adapter.convert(source, target, {"quality": 50})

        # Single page is saved directly to target_path
        assert target.exists()
        assert target.stat().st_size > 0


def _create_test_pdf(path: Path, pages: int = 1):
    doc = fitz.open()
    for _ in range(pages):
        page = doc.new_page()
        page.insert_text((50, 50), f"Test page {page.number + 1}")
    doc.save(str(path))
    doc.close()
