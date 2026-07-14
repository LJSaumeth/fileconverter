from abc import ABC, abstractmethod

from domain.entities import ConversionProgress


class ProgressNotifierPort(ABC):
    @abstractmethod
    async def notify(self, progress: ConversionProgress) -> None:
        raise NotImplementedError
