import os
import shutil
from pathlib import Path
from typing import Optional
import aiofiles
from uuid import uuid4

from app.config import settings


class StorageService:
    def __init__(self):
        self.uploads_path = Path(settings.UPLOADS_PATH)
        self.outputs_path = Path(settings.OUTPUTS_PATH)
        self.previews_path = Path(settings.PREVIEWS_PATH)

        self.uploads_path.mkdir(parents=True, exist_ok=True)
        self.outputs_path.mkdir(parents=True, exist_ok=True)
        self.previews_path.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, content: bytes, original_filename: str) -> str:
        ext = Path(original_filename).suffix.lower()
        filename = f"{uuid4()}{ext}"
        file_path = self.uploads_path / filename

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return filename

    async def save_output(self, job_id: str, content: bytes, file_type: str) -> str:
        job_output_path = self.outputs_path / job_id
        job_output_path.mkdir(parents=True, exist_ok=True)

        filename = f"model.{file_type}"
        file_path = job_output_path / filename

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return str(file_path)

    def save_output_sync(self, job_id: str, content: bytes, file_type: str) -> str:
        job_output_path = self.outputs_path / job_id
        job_output_path.mkdir(parents=True, exist_ok=True)

        filename = f"model.{file_type}"
        file_path = job_output_path / filename

        with open(file_path, "wb") as f:
            f.write(content)

        return str(file_path)

    async def save_preview(self, job_id: str, content: bytes) -> str:
        filename = f"{job_id}.png"
        file_path = self.previews_path / filename

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return str(file_path)

    def save_preview_sync(self, job_id: str, content: bytes) -> str:
        filename = f"{job_id}.png"
        file_path = self.previews_path / filename

        with open(file_path, "wb") as f:
            f.write(content)

        return str(file_path)

    def get_upload_path(self, filename: str) -> Optional[Path]:
        file_path = self.uploads_path / filename
        if file_path.exists():
            return file_path
        return None

    def get_output_path(self, job_id: str, file_type: str) -> Optional[Path]:
        file_path = self.outputs_path / job_id / f"model.{file_type}"
        if file_path.exists():
            return file_path
        return None

    def get_preview_path(self, job_id: str) -> Optional[Path]:
        file_path = self.previews_path / f"{job_id}.png"
        if file_path.exists():
            return file_path
        return None

    def cleanup_job(self, job_id: str):
        job_output_path = self.outputs_path / job_id
        if job_output_path.exists():
            shutil.rmtree(job_output_path)

        preview_path = self.previews_path / f"{job_id}.png"
        if preview_path.exists():
            preview_path.unlink()

    def get_file_size(self, file_path: Path) -> int:
        if file_path.exists():
            return file_path.stat().st_size
        return 0


storage_service = StorageService()
