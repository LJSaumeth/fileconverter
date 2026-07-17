from abc import ABC, abstractmethod

from domain.entities import ConversionJob, ConversionResult
from domain.ports.output.progress_notifier_port import ProgressNotifierPort


class ConvertFileUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        job: ConversionJob,
        progress_notifier: ProgressNotifierPort | None = None,
    ) -> ConversionResult:
        """Execute a file conversion.

        Args:
            job: The conversion job to execute.
            progress_notifier: Optional notifier for real-time progress
                reporting (e.g. via WebSocket).

        Returns:
            A ``ConversionResult`` with the outcome.
        """
        raise NotImplementedError
