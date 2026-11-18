from typing import Literal

from pydantic import BaseModel, Field

class DownloadRequest(BaseModel):
    url: str = Field(..., examples=["https://www.youtube.com/watch?v=..."])
    kind: Literal["audio", "video"] = "audio"
    quality: str = "best"

class DownloadResponse(BaseModel):
    status: str
    message: str
    kind: Literal["audio", "video"]
    filename: str
    download_url: str
    filesize_mb: float | None = None