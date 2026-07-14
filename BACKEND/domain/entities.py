from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from uuid import UUID


class FileFormat(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    PNG = "png"
    JPG = "jpg"


class ConversionStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ConversionJob:
    job_id: UUID
    source_path: Path
    source_format: FileFormat
    target_format: FileFormat
    options: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ConversionResult:
    job_id: UUID
    status: ConversionStatus
    output_path: Path | None
    error_message: str | None = None


@dataclass(frozen=True)
class ConversionProgress:
    job_id: UUID
    percentage: int
    status: ConversionStatus
    message: str | None = None


class ConversionError(Exception):
    def __init__(self, message: str, job_id: UUID | None = None):
        self.job_id = job_id
        super().__init__(message)


class UnsupportedConversionError(ConversionError):
    pass
