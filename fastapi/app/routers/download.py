from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.schemas.download import DownloadRequest, DownloadResponse
from app.services.ytdlp import download_youtube_audio

router = APIRouter()

@router.post("/download", response_model=DownloadResponse)
async def download_music(request: DownloadRequest):
    try:
        file_path = Path(await download_youtube_audio(request.url, request.quality))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

    if not file_path.is_file():
        raise HTTPException(500, f"Файл не создан: {file_path.name}")

    return DownloadResponse(
        status="success",
        message="Готово",
        filename=file_path.name,
        download_url=f"/api/download/file/{file_path.name}",
    )


@router.get("/download/file/{filename}")
async def get_file(filename: str):
    # защита от ../../etc/passwd
    safe_name = Path(filename).name
    file_path = (settings.download_dir / safe_name).resolve()

    if not file_path.is_relative_to(settings.download_dir.resolve()):
        raise HTTPException(400, "Недопустимое имя файла")
    if not file_path.is_file():
        raise HTTPException(404, "Файл не найден")

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=safe_name,      # Starlette сам ставит Content-Disposition: attachment
    )