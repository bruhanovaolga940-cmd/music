from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # откуда читать переменные
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",              # лишние переменные в .env не роняют приложение
    )

    # --- общее ---
    app_name: str = "YouTube Music Downloader API"
    debug: bool = False

    # --- пути ---
    base_dir: Path = PROJECT_ROOT
    downloads_dir: Path | None = None   # если None — берём base_dir/downloads

    # --- аудио ---
    audio_format: str = "mp3"
    audio_quality: str = "192"          # kbps для mp3
    default_quality: str = "best"

    # --- JS-рантайм (Deno/Node) ---
    js_runtime_path: str | None = None

    # --- видео ---
    video_container: str = "mp4"
    default_video_height: int = 1080
    max_video_height: int = 2160
    max_filesize_mb: int = 500

    # --- ограничения ---
    max_duration_seconds: int = 1800    # 30 минут на трек
    max_file_age_hours: int = 24        # через сколько чистить папку

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- ffmpeg (если не в PATH) ---
    ffmpeg_location: str | None = None

    cookies_file: str | None = None
    cookies_from_browser: str | None = None
    cookies_b64: str | None = None

    @property
    def download_dir(self) -> Path:
        """Папка скачиваний, создаётся при первом обращении."""
        path = self.downloads_dir or self.base_dir / "downloads"
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()