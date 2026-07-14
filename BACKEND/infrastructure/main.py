
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.input.http.conversion_router import router
from adapters.output.storage.local_file_storage_adapter import LocalFileStorageAdapter
from application.use_cases.convert_file import ConvertFileService
from application.use_cases.list_supported_conversions import (
    ListSupportedConversionsService,
)
from domain.entities import ConversionError, FileFormat
from domain.ports.output.converter_registry_port import ConverterRegistryPort
from domain.ports.output.file_converter_port import FileConverterPort
from infrastructure.config import settings


class ConverterRegistry(ConverterRegistryPort):
    def __init__(self, converters: list[FileConverterPort]):
        self._converters = converters

    def get_converter(self, source: FileFormat, target: FileFormat) -> FileConverterPort:
        for converter in self._converters:
            if converter.supports(source, target):
                return converter
        raise ConversionError(
            f"No converter found for {source.value} -> {target.value}"
        )


def create_app() -> FastAPI:
    app = FastAPI(title="FileConverter Backend", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _wiring(app)
    app.include_router(router)
    return app


def _wiring(app: FastAPI) -> None:
    file_storage = LocalFileStorageAdapter(settings.temp_dir)

    converters = _create_converters()
    converter_registry = ConverterRegistry(converters)

    convert_use_case = ConvertFileService(converter_registry, file_storage)
    list_use_case = ListSupportedConversionsService(converters)

    app.state.convert_use_case = convert_use_case
    app.state.list_use_case = list_use_case
    app.state.file_storage = file_storage


def _create_converters() -> list[FileConverterPort]:
    converters: list[FileConverterPort] = []

    try:
        from adapters.output.converters.pdf_to_image_adapter import PdfToImageAdapter

        converters.append(PdfToImageAdapter(settings))
    except ImportError:
        pass

    try:
        from adapters.output.converters.image_to_pdf_adapter import ImageToPdfAdapter

        converters.append(ImageToPdfAdapter(settings))
    except ImportError:
        pass

    try:
        from adapters.output.converters.office_to_pdf_adapter import OfficeToPdfAdapter

        converters.append(OfficeToPdfAdapter(settings))
    except ImportError:
        pass

    try:
        from adapters.output.converters.pdf_to_docx_adapter import PdfToDocxAdapter

        converters.append(PdfToDocxAdapter(settings))
    except ImportError:
        pass

    try:
        from adapters.output.converters.pdf_to_docx_ocr_adapter import (
            PdfToDocxOcrAdapter,
        )

        converters.append(PdfToDocxOcrAdapter(settings))
    except ImportError:
        pass

    return converters


def main():
    uvicorn.run(
        "infrastructure.main:create_app",
        host=settings.host,
        port=settings.port,
        factory=True,
        reload=False,
    )


if __name__ == "__main__":
    main()
