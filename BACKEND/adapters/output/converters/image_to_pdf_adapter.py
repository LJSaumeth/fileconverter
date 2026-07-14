from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfgen import canvas

from domain.entities import ConversionError, FileFormat
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import Settings

PAGE_SIZES = {
    "A4": A4,
    "a4": A4,
    "Letter": LETTER,
    "letter": LETTER,
}


class ImageToPdfAdapter(FileConverterPort):
    def __init__(self, settings: Settings):
        self._settings = settings

    def supports(self, source: FileFormat, target: FileFormat) -> bool:
        return source in (FileFormat.PNG, FileFormat.JPG) and target == FileFormat.PDF

    def convert(self, source_path: Path, target_path: Path, options: dict) -> None:
        image_files = self._resolve_image_files(source_path, options)

        if not image_files:
            raise ConversionError("At least one image must be provided")

        page_size = self._parse_page_size(options)
        orientation = options.get("orientation", "portrait")
        fit_mode = options.get("fit", "inside")

        if orientation == "landscape":
            page_size = (page_size[1], page_size[0])

        c = canvas.Canvas(str(target_path), pagesize=page_size)

        try:
            for image_path in image_files:
                self._add_image_page(c, image_path, page_size, fit_mode)

            c.save()
        except Exception as e:
            raise ConversionError(f"Failed to create PDF: {e}") from e

    def _add_image_page(
        self, c: canvas.Canvas, image_path: Path, page_size: tuple, fit_mode: str
    ):
        try:
            img = Image.open(image_path)
        except Exception as e:
            raise ConversionError(
                f"Could not open image {image_path.name}: {e}"
            ) from e

        img = ImageOps.exif_transpose(img)

        if img.mode in ("RGBA", "LA", "P"):
            if img.mode == "P":
                img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img)
            img = background

        max_dim = self._settings.max_image_dimension
        if img.width > max_dim or img.height > max_dim:
            ratio = max_dim / max(img.width, img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        temp_jpg = image_path.parent / f"_temp_{image_path.stem}.jpg"
        img.save(temp_jpg, "JPEG", quality=95)

        if fit_mode == "inside":
            page_w, page_h = page_size
            margin = 20
            avail_w = page_w - 2 * margin
            avail_h = page_h - 2 * margin

            scale = min(avail_w / img.width, avail_h / img.height, 1.0)
            draw_w = img.width * scale
            draw_h = img.height * scale

            x = (page_w - draw_w) / 2
            y = (page_h - draw_h) / 2

            c.drawImage(str(temp_jpg), x, y, width=draw_w, height=draw_h)
        else:
            c.drawImage(
                str(temp_jpg), 0, 0, width=page_size[0], height=page_size[1]
            )

        c.showPage()
        temp_jpg.unlink(missing_ok=True)

    def _resolve_image_files(self, source_path: Path, options: dict) -> list[Path]:
        image_list = options.get("image_files")
        if image_list:
            return [Path(p) for p in image_list]
        return [source_path]

    def _parse_page_size(self, options: dict) -> tuple:
        page_size_name = options.get("page_size")
        if page_size_name and page_size_name in PAGE_SIZES:
            return PAGE_SIZES[page_size_name]

        if page_size_name == "fit" or page_size_name is None:
            return A4

        return A4
