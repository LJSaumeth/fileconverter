from domain.entities import FileFormat
from domain.ports.input.list_supported_conversions_use_case import (
    ListSupportedConversionsUseCase,
)
from domain.ports.output.file_converter_port import FileConverterPort


class ListSupportedConversionsService(ListSupportedConversionsUseCase):
    def __init__(
        self,
        converters: list[FileConverterPort],
    ):
        self._converters = converters

    def execute(self) -> dict[FileFormat, list[FileFormat]]:
        result: dict[FileFormat, set[FileFormat]] = {}

        for source in FileFormat:
            for target in FileFormat:
                if source == target:
                    continue
                for converter in self._converters:
                    if converter.supports(source, target):
                        result.setdefault(source, set()).add(target)

        return {k: sorted(v, key=lambda f: f.value) for k, v in result.items()}
