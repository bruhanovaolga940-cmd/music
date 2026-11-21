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


def _build_opts(kind: str, quality: str) -> dict:
    def _progress(d):
        if d["status"] == "downloading":
            print(f"{d.get('_percent_str', '').strip()} {d.get('_speed_str', '').strip()} ETA {d.get('_eta_str', '').strip()}", flush=True)
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
        "noprogress": True,

    }

    if settings.ffmpeg_location:
        opts["ffmpeg_location"] = settings.ffmpeg_location
    if settings.js_runtime_path:
        opts["js_runtimes"] = {"deno": {"path": settings.js_runtime_path}}
    if settings.cookies_file:
        opts["cookiefile"] = str(settings.base_dir / settings.cookies_file)
    elif settings.cookies_from_browser:
        opts["cookiesfrombrowser"] = (settings.cookies_from_browser,)
    elif settings.cookies_b64:
        opts["cookiefile"] = str(settings.base_dir / "cookies.txt")

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


def download_media(url: str, kind: str = "audio", quality: str = "best") -> Path:
    opts = _build_opts(kind, quality)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(info["requested_downloads"][0]["filepath"])

    if not path.is_file():
        raise RuntimeError("Файл не создан")
    return path