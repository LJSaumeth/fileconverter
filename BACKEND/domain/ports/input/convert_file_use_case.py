from abc import ABC, abstractmethod

from domain.entities import ConversionJob, ConversionResult


class ConvertFileUseCase(ABC):
    @abstractmethod
    def execute(self, job: ConversionJob) -> ConversionResult:
        raise NotImplementedError
