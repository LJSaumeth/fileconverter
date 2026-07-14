from abc import ABC, abstractmethod

from domain.entities import FileFormat


class ListSupportedConversionsUseCase(ABC):
    @abstractmethod
    def execute(self) -> dict[FileFormat, list[FileFormat]]:
        raise NotImplementedError
