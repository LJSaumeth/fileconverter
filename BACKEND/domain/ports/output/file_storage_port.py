from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID


class FileStoragePort(ABC):
    @abstractmethod
    def save_temp_file(self, job_id: UUID, content: bytes, filename: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def get_output_path(self, job_id: UUID, target_format: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def cleanup(self, job_id: UUID) -> None:
        raise NotImplementedError
