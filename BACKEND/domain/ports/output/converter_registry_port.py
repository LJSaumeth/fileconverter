from abc import ABC, abstractmethod

from domain.entities import FileFormat
from domain.ports.output.file_converter_port import FileConverterPort


class ConverterRegistryPort(ABC):
    @abstractmethod
    def get_converter(self, source: FileFormat, target: FileFormat) -> FileConverterPort:
        raise NotImplementedError
