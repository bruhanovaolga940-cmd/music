import base64
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers.download import router as download_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.download_dir          # создаст папку на старте
    if settings.cookies_b64:
        path = settings.base_dir / "cookies.txt"
        path.write_bytes(base64.b64decode(settings.cookies_b64))
        settings.cookies_file = "cookies.txt"
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Запрещаем поисковикам индексировать сайт, API и файлы
@app.middleware("http")
async def add_noindex_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return "User-agent: *\nDisallow: /"


# Маршруты API (обязательно должны идти ДО раздачи статики)
app.include_router(download_router, prefix="/api", tags=["download"])

# Раздача собранного React-фронтенда в продакшене (Railway)
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
