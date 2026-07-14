import json
from uuid import uuid4

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from domain.entities import ConversionJob, FileFormat
from domain.ports.input.convert_file_use_case import ConvertFileUseCase
from domain.ports.input.list_supported_conversions_use_case import (
    ListSupportedConversionsUseCase,
)
from domain.ports.output.file_storage_port import FileStoragePort

router = APIRouter(prefix="/api", tags=["conversion"])


def _get_convert_use_case(request: Request) -> ConvertFileUseCase:
    return request.app.state.convert_use_case


def _get_list_use_case(request: Request) -> ListSupportedConversionsUseCase:
    return request.app.state.list_use_case


def _get_file_storage(request: Request) -> FileStoragePort:
    return request.app.state.file_storage


@router.post("/convert")
async def convert_file(
    request: Request,
    file: UploadFile = File(...),  # noqa: B008
    source_format: str = Form(...),  # noqa: B008
    target_format: str = Form(...),  # noqa: B008
    options: str = Form(default="{}"),  # noqa: B008
):
    try:
        src_fmt = FileFormat(source_format.lower())
        tgt_fmt = FileFormat(target_format.lower())
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "error": (
                    f"Unsupported format. "
                    f"Source: {source_format}, Target: {target_format}"
                )
            },
        )

    try:
        parsed_options = json.loads(options)
    except json.JSONDecodeError:
        parsed_options = {}

    storage = _get_file_storage(request)
    job_id = uuid4()
    content_bytes = await file.read()

    source_path = storage.save_temp_file(job_id, content_bytes, file.filename or "input")

    use_case = _get_convert_use_case(request)
    job = ConversionJob(
        job_id=job_id,
        source_path=source_path,
        source_format=src_fmt,
        target_format=tgt_fmt,
        options=parsed_options,
    )

    result = use_case.execute(job)

    if result.status.value == "failed":
        return JSONResponse(
            status_code=422,
            content={"job_id": str(result.job_id), "error": result.error_message},
        )

    return FileResponse(
        path=str(result.output_path),
        filename=result.output_path.name,
        media_type="application/octet-stream",
    )


@router.get("/conversions")
async def list_supported_conversions(request: Request):
    use_case = _get_list_use_case(request)
    result = use_case.execute()
    return {
        source.value: [target.value for target in targets]
        for source, targets in result.items()
        if targets
    }
