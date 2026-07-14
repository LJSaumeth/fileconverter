from pathlib import Path
from uuid import UUID

from domain.ports.output.file_storage_port import FileStoragePort


class LocalFileStorageAdapter(FileStoragePort):
    def __init__(self, temp_dir: Path):
        self._temp_dir = temp_dir
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    def save_temp_file(self, job_id: UUID, content: bytes, filename: str) -> Path:
        job_dir = self._temp_dir / str(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        file_path = job_dir / filename
        file_path.write_bytes(content)
        return file_path

    def get_output_path(self, job_id: UUID, target_format: str) -> Path:
        job_dir = self._temp_dir / str(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir / f"output.{target_format}"

    def cleanup(self, job_id: UUID) -> None:
        import shutil

        job_dir = self._temp_dir / str(job_id)
        if job_dir.exists():
            shutil.rmtree(job_dir)
