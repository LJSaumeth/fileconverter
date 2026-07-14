from pathlib import Path

import pytest
from PIL import Image

from adapters.output.converters.image_to_pdf_adapter import ImageToPdfAdapter
from domain.entities import ConversionError, FileFormat


class TestImageToPdfAdapter:
    def test_supports_png_to_pdf(self, settings):
        adapter = ImageToPdfAdapter(settings)
        assert adapter.supports(FileFormat.PNG, FileFormat.PDF) is True

    def test_supports_jpg_to_pdf(self, settings):
        adapter = ImageToPdfAdapter(settings)
        assert adapter.supports(FileFormat.JPG, FileFormat.PDF) is True

    def test_does_not_support_unsupported_target(self, settings):
        adapter = ImageToPdfAdapter(settings)
        assert adapter.supports(FileFormat.PNG, FileFormat.DOCX) is False

    def test_convert_single_png_to_pdf(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        source = tmp_path / "test.png"
        target = tmp_path / "output.pdf"
        _create_test_image(source, size=(800, 600))

        adapter.convert(source, target, {})

        assert target.exists()
        assert target.stat().st_size > 0

    def test_convert_single_jpg_to_pdf(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        source = tmp_path / "test.jpg"
        target = tmp_path / "output.pdf"
        _create_test_image(source, size=(800, 600), fmt="JPEG")

        adapter.convert(source, target, {})

        assert target.exists()
        assert target.stat().st_size > 0

    def test_convert_multiple_images_to_pdf(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        img1 = tmp_path / "img1.png"
        img2 = tmp_path / "img2.png"
        img3 = tmp_path / "img3.jpg"
        _create_test_image(img1, size=(800, 600))
        _create_test_image(img2, size=(400, 300))
        _create_test_image(img3, size=(1024, 768), fmt="JPEG")
        target = tmp_path / "output.pdf"

        adapter.convert(
            img1, target, {"image_files": [str(img1), str(img2), str(img3)]}
        )

        assert target.exists()
        assert target.stat().st_size > 0

    def test_corrupted_image_raises_error(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        source = tmp_path / "invalid.png"
        source.write_text("not an image")
        target = tmp_path / "output.pdf"

        with pytest.raises(ConversionError, match="Could not open image"):
            adapter.convert(source, target, {})

    def test_a4_page_size(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        source = tmp_path / "test.png"
        _create_test_image(source, size=(400, 300))
        target = tmp_path / "output.pdf"

        adapter.convert(source, target, {"page_size": "A4"})

        assert target.exists()

    def test_landscape_orientation(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        source = tmp_path / "test.png"
        _create_test_image(source, size=(400, 300))
        target = tmp_path / "output.pdf"

        adapter.convert(source, target, {"orientation": "landscape"})

        assert target.exists()

    def test_fit_inside_scales_image(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        source = tmp_path / "test.png"
        _create_test_image(source, size=(4000, 3000))
        target = tmp_path / "output.pdf"

        adapter.convert(source, target, {"page_size": "A4", "fit": "inside"})

        assert target.exists()

    def test_image_with_alpha_channel(self, settings, tmp_path):
        adapter = ImageToPdfAdapter(settings)
        source = tmp_path / "rgba.png"
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        img.save(source)
        target = tmp_path / "output.pdf"

        adapter.convert(source, target, {})

        assert target.exists()


def _create_test_image(path: Path, size=(400, 300), fmt="PNG"):
    img = Image.new("RGB", size, color=(100, 150, 200))
    img.save(path, format=fmt)
