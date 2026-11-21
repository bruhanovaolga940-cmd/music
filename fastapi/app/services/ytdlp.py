import asyncio
import tempfile
from pathlib import Path

import yt_dlp

from app.config import settings

AUDIO_BITRATE = {"best": "0", "medium": "192", "low": "128"}
VIDEO_HEIGHT = {"best": None, "2160": 2160, "1080": 1080, "720": 720, "480": 480}


def _video_format(height: int | None) -> str:
    if height:
        return (
            f"bv*[height<={height}][ext=mp4]+ba[ext=m4a]/"
            f"bv*[height<={height}]+ba/"
            f"b[height<={height}]/b"
        )
    return "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b"


def _build_opts(kind: str, quality: str, cookie_path: Path | None = None) -> dict:
    def _progress(d):
        if d["status"] == "downloading":
            print(
                f"{d.get('_percent_str', '').strip()} "
                f"{d.get('_speed_str', '').strip()} "
                f"ETA {d.get('_eta_str', '').strip()}",
                flush=True,
            )
        elif d["status"] == "finished":
            print("Скачано, идёт склейка...", flush=True)

    opts: dict = {
        "outtmpl": str(settings.download_dir / "%(title).150B [%(id)s].%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "color": "no_color",
        "max_filesize": settings.max_filesize_mb * 1024 * 1024,
        "restrictfilenames": False,
        "windowsfilenames": True,
        "noplaylist": True,
        "progress_hooks": [_progress],
    }

    if settings.ffmpeg_location:
        opts["ffmpeg_location"] = settings.ffmpeg_location
    if settings.js_runtime_path:
        opts["js_runtimes"] = {"deno": {"path": settings.js_runtime_path}}
    if cookie_path:
        opts["cookiefile"] = str(cookie_path)

    if kind == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": AUDIO_BITRATE.get(quality, "0"),
        }]
    else:
        height = VIDEO_HEIGHT.get(quality, settings.default_video_height)
        if height and height > settings.max_video_height:
            height = settings.max_video_height
        opts["format"] = _video_format(height)
        opts["merge_output_format"] = settings.video_container

    return opts


def _create_temp_cookies() -> Path | None:
    raw_cookies = getattr(settings, "youtube_cookies", None)
    if not raw_cookies:
        return None

    # Восстанавливаем переносы строк, если Railway передал их как текст \n
    normalized = raw_cookies.replace("\\r\\n", "\n").replace("\\n", "\n").strip() + "\n"

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    tmp.write(normalized)
    tmp.close()
    return Path(tmp.name)


def download_media_sync(url: str, kind: str = "audio", quality: str = "best") -> Path:
    cookie_path = _create_temp_cookies()
    try:
        opts = _build_opts(kind, quality, cookie_path=cookie_path)

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info or "requested_downloads" not in info:
                raise RuntimeError("Не удалось получить поток для скачивания")
            path = Path(info["requested_downloads"][0]["filepath"])

        if not path.is_file():
            raise RuntimeError("Файл не создан")
        return path
    finally:
        if cookie_path and cookie_path.exists():
            cookie_path.unlink(missing_ok=True)


async def download_media(url: str, kind: str = "audio", quality: str = "best") -> Path:
    return await asyncio.to_thread(download_media_sync, url, kind, quality)
