import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    temp_dir: Path = Path("temp")
    host: str = "127.0.0.1"
    port: int = 0
    conversion_timeout_seconds: int = 120
    office_to_pdf_timeout_seconds: int = 180
    pdf_to_docx_timeout_seconds: int = 180
    default_image_dpi: int = 150
    max_image_dimension: int = 5000
    libreoffice_path: str | None = None

    def __post_init__(self):
        for field_name in self.__dataclass_fields__:
            env_key = f"FC_{field_name.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                field_type = type(getattr(self, field_name))
                if field_type is int:
                    setattr(self, field_name, int(env_val))
                elif field_type is Path:
                    setattr(self, field_name, Path(env_val))
                else:
                    setattr(self, field_name, env_val)


settings = Settings()
