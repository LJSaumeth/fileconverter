from abc import ABC, abstractmethod
from pathlib import Path

from domain.entities import FileFormat


class FileConverterPort(ABC):
    @abstractmethod
    def supports(self, source: FileFormat, target: FileFormat) -> bool:
        raise NotImplementedError

    @abstractmethod
    def convert(self, source_path: Path, target_path: Path, options: dict) -> None:
        raise NotImplementedError
