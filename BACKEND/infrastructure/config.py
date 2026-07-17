import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    # ── Server ──────────────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 0

    # Comma-separated list of allowed origins, or "*" for any.
    # Examples: "*" | "http://localhost:5173,http://localhost:3000"
    cors_origins: str = "*"

    # ── File handling ────────────────────────────────────────────────
    temp_dir: Path = Path("temp")
    max_file_size_mb: int = 100
    max_file_size_bytes: int = 104_857_600  # computed from max_file_size_mb

    # ── Conversion defaults ──────────────────────────────────────────
    conversion_timeout_seconds: int = 120
    office_to_pdf_timeout_seconds: int = 180
    pdf_to_docx_timeout_seconds: int = 180
    default_image_dpi: int = 150
    max_image_dimension: int = 5000

    # Number of pages after which PDF → image produces a ZIP instead of
    # individual files. Set to 0 to always produce individual files.
    zip_threshold: int = 6

    # ── External tool paths ──────────────────────────────────────────
    # Explicit path to LibreOffice soffice binary. Leave as None for
    # auto-detection (see OfficeToPdfAdapter._find_libreoffice).
    libreoffice_path: str | None = None

    # Explicit path to Tesseract binary. Leave as None for auto-detection
    # via shutil.which("tesseract").
    tesseract_path: str | None = None

    # ── Observability ────────────────────────────────────────────────
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        for field_name in self.__dataclass_fields__:
            env_key = f"FC_{field_name.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                field_type = type(getattr(self, field_name))
                if field_type is int:
                    setattr(self, field_name, int(env_val))
                elif field_type is Path:
                    setattr(self, field_name, Path(env_val))
                elif field_type is bool:
                    setattr(self, field_name, env_val.lower() in ("1", "true", "yes"))
                else:
                    setattr(self, field_name, env_val)

        self.max_file_size_bytes = self.max_file_size_mb * 1024 * 1024


settings = Settings()
