import zipfile
from pathlib import Path

import fitz

from domain.entities import ConversionError, FileFormat
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import Settings

PageSpec = tuple[int, int] | list[int] | None


class PdfToImageAdapter(FileConverterPort):
    SUPPORTED_TARGETS = {FileFormat.PNG, FileFormat.JPG}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def supports(self, source: FileFormat, target: FileFormat) -> bool:
        return source == FileFormat.PDF and target in self.SUPPORTED_TARGETS

    def convert(self, source_path: Path, target_path: Path, options: dict) -> None:
        dpi = self._parse_dpi(options)
        quality = self._parse_quality(options)
        pages = self._parse_pages(options)

        try:
            doc = fitz.open(source_path)
        except Exception as e:
            raise ConversionError(f"Could not open PDF: {e}") from e

        if doc.page_count == 0:
            doc.close()
            raise ConversionError("The PDF contains no pages to convert")

        page_indices = self._resolve_page_indices(pages, doc.page_count)
        total_pages = len(page_indices)
        use_zip = total_pages >= self._settings.zip_threshold

        if use_zip:
            output_dir = target_path.parent / f"{target_path.stem}_images"
            output_dir.mkdir(parents=True, exist_ok=True)
            image_paths: list[Path] = []

            try:
                stem = source_path.stem
                for _i, page_num in enumerate(page_indices):
                    page = doc[page_num]
                    ext = self._resolve_ext(target_path)
                    image_path = output_dir / f"{stem}_page_{page_num + 1}.{ext}"
                    self._render_page(page, image_path, dpi, quality, ext)
                    image_paths.append(image_path)

                self._create_zip(image_paths, target_path)

                for p in image_paths:
                    p.unlink(missing_ok=True)
                output_dir.rmdir()
            except Exception:
                for p in image_paths:
                    p.unlink(missing_ok=True)
                output_dir.rmdir()
                raise
        else:
            try:
                for i, page_num in enumerate(page_indices):
                    page = doc[page_num]
                    ext = self._resolve_ext(target_path)
                    # When there is only one page, save directly to the
                    # requested target_path so the HTTP layer can serve
                    # the file via FileResponse without guessing names.
                    if total_pages == 1:
                        out = target_path
                    else:
                        out = (
                            target_path.parent
                            / f"{target_path.stem}_page_{page_num + 1}.{ext}"
                        )
                    self._render_page(page, out, dpi, quality, ext)
            except Exception:
                stem = source_path.stem
                for p in target_path.parent.glob(f"{stem}_page_*"):
                    p.unlink(missing_ok=True)
                raise

        doc.close()

    def _render_page(self, page, output_path: Path, dpi: int, quality: int, ext: str):
        try:
            pix = page.get_pixmap(dpi=dpi)
            if ext == "jpg":
                pix.pil_save(str(output_path), optimize=True, quality=quality)
            else:
                pix.save(str(output_path))
        except Exception as e:
            raise ConversionError(
                f"Failed to render page {page.number + 1}: {e}"
            ) from e

    def _create_zip(self, image_paths: list[Path], zip_path: Path):
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in image_paths:
                zf.write(p, p.name)

    def _resolve_page_indices(self, pages: PageSpec, total_pages: int) -> list[int]:
        if pages is None:
            return list(range(total_pages))

        if isinstance(pages, tuple) and len(pages) == 2:
            start, end = pages
            if start > end:
                start, end = end, start
            start = max(1, start) - 1
            end = min(total_pages, end)
            if start >= total_pages or end <= 0 or start >= end:
                raise ConversionError(
                    f"Page range {pages[0]}-{pages[1]} is outside the document "
                    f"(total pages: {total_pages})"
                )
            return list(range(start, end))

        if isinstance(pages, list):
            indices = []
            for p in pages:
                if p < 1 or p > total_pages:
                    raise ConversionError(
                        f"Page {p} is outside the document (total pages: {total_pages})"
                    )
                indices.append(p - 1)
            return indices

        return list(range(total_pages))

    def _parse_dpi(self, options: dict) -> int:
        dpi = options.get("dpi", self._settings.default_image_dpi)
        dpi = int(dpi)
        return max(72, min(600, dpi))

    def _parse_quality(self, options: dict) -> int:
        quality = options.get("quality", 85)
        quality = int(quality)
        return max(1, min(100, quality))

    def _parse_pages(self, options: dict) -> PageSpec:
        pages = options.get("pages")
        if pages is None:
            return None
        if isinstance(pages, list):
            return [int(p) for p in pages]
        if isinstance(pages, tuple) and len(pages) == 2:
            return (int(pages[0]), int(pages[1]))
        return None

    def _resolve_ext(self, target_path: Path) -> str:
        ext = target_path.suffix.lstrip(".")
        if ext in ("png", "jpg", "jpeg"):
            return "jpg" if ext in ("jpg", "jpeg") else ext
        return "png"
