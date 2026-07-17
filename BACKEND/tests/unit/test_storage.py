from uuid import uuid4

from adapters.output.storage.local_file_storage_adapter import (
    LocalFileStorageAdapter,
)


class TestLocalFileStorageAdapter:
    """Tests for the local filesystem-based storage adapter."""

    def test_save_temp_file_creates_file(self, tmp_path):
        storage = LocalFileStorageAdapter(tmp_path / "temp")
        job_id = uuid4()
        content = b"test file content"

        saved_path = storage.save_temp_file(job_id, content, "input.pdf")

        assert saved_path.exists()
        assert saved_path.read_bytes() == content
        assert saved_path.name == "input.pdf"

    def test_get_output_path_returns_path(self, tmp_path):
        storage = LocalFileStorageAdapter(tmp_path / "temp")
        job_id = uuid4()

        output_path = storage.get_output_path(job_id, "pdf")

        assert str(output_path).endswith(".pdf")
        assert str(job_id) in str(output_path)

    def test_get_output_path_creates_directory(self, tmp_path):
        storage = LocalFileStorageAdapter(tmp_path / "temp")
        job_id = uuid4()

        output_path = storage.get_output_path(job_id, "png")

        assert output_path.parent.exists()

    def test_cleanup_removes_job_directory(self, tmp_path):
        storage = LocalFileStorageAdapter(tmp_path / "temp")
        job_id = uuid4()

        # Create a file first
        storage.save_temp_file(job_id, b"data", "test.txt")
        job_dir = tmp_path / "temp" / str(job_id)
        assert job_dir.exists()

        storage.cleanup(job_id)
        assert not job_dir.exists()

    def test_cleanup_idempotent(self, tmp_path):
        storage = LocalFileStorageAdapter(tmp_path / "temp")
        job_id = uuid4()

        # Cleanup on non-existent job should not raise
        storage.cleanup(job_id)  # must not raise

    def test_multiple_jobs_isolated(self, tmp_path):
        storage = LocalFileStorageAdapter(tmp_path / "temp")
        job_a = uuid4()
        job_b = uuid4()

        storage.save_temp_file(job_a, b"content a", "a.txt")
        storage.save_temp_file(job_b, b"content b", "b.txt")

        # Cleanup job_a only
        storage.cleanup(job_a)

        job_a_dir = tmp_path / "temp" / str(job_a)
        job_b_dir = tmp_path / "temp" / str(job_b)

        assert not job_a_dir.exists()
        assert job_b_dir.exists()
        assert (job_b_dir / "b.txt").read_bytes() == b"content b"

    def test_temp_dir_created_on_init(self, tmp_path):
        custom_dir = tmp_path / "my_temp"
        assert not custom_dir.exists()

        LocalFileStorageAdapter(custom_dir)

        assert custom_dir.exists()
