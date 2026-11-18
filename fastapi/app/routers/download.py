import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool

from app.config import settings
from app.schemas.download import DownloadRequest, DownloadResponse
from app.services.ytdlp import download_media

router = APIRouter()


@router.post("/download", response_model=DownloadResponse)
async def download(request: DownloadRequest):
    try:
        path = await run_in_threadpool(download_media, request.url, request.kind, request.quality)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e).replace("\x1b[0;31m", "").replace("\x1b[0m", ""))

    return DownloadResponse(
        status="success",
        message="Готово",
        kind=request.kind,
        filename=path.name,
        download_url=f"/api/download/file/{path.name}",
        filesize_mb=round(path.stat().st_size / 1024 / 1024, 1),
    )


@router.get("/download/file/{filename}")
async def get_file(filename: str):
    safe_name = Path(filename).name
    file_path = (settings.download_dir / safe_name).resolve()

    if not file_path.is_relative_to(settings.download_dir.resolve()):
        raise HTTPException(400, "Недопустимое имя файла")
    if not file_path.is_file():
        raise HTTPException(404, "Файл не найден")

    media_type = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"

    return FileResponse(path=file_path, media_type=media_type, filename=safe_name)