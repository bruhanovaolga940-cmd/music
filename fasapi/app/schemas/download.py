from pydantic import BaseModel
from typing import Optional

class DownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "best"          # best, medium, low

class DownloadResponse(BaseModel):
    status: str
    message: str
    filename: str
    download_url: str