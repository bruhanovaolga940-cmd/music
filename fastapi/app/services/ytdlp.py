import asyncio
import uuid
import yt_dlp
from app.config import settings

QUALITY_MAP = {
    "best": "320",
    "medium": "192",
    "low": "128",
}


def _sync_download(url: str, quality: str) -> str:
    bitrate = QUALITY_MAP.get(quality, settings.audio_quality)
    # Добавляем короткий уникальный суффикс, чтобы одинаковые треки не конфликтовали
    uid = uuid.uuid4().hex[:6]

    opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": settings.audio_format,
            "preferredquality": bitrate,
        }],
        "outtmpl": str(settings.download_dir / f"%(title).80s_{uid}.%(ext)s"),
        "socket_timeout": 15,         # Не ждем зависшее соединение вечно
        "retries": 3,                 # Максимум 3 повтора при сбое сети
        "quiet": False,               # Временно включаем логи в консоль для диагностики
        "no_warnings": False,
        "noprogress": True,
        "match_filter": yt_dlp.utils.match_filter_func(
            f"duration < {settings.max_duration_seconds}"
        ),
    }

    if settings.ffmpeg_location:
        opts["ffmpeg_location"] = settings.ffmpeg_location

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Проверяем, не отфильтровалось ли видео по длительности
    if not info or "requested_downloads" not in info:
        raise ValueError("Видео не подходит под ограничения (например, длиннее 30 минут)")

    return info["requested_downloads"][0]["filepath"]


async def download_youtube_audio(url: str, quality: str = "best") -> str:
    # Запускаем синхронный yt-dlp в отдельном потоке, чтобы не вешать FastAPI
    return await asyncio.to_thread(_sync_download, url, quality)
