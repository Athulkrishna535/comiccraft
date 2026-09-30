from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routes import router


settings = get_settings()

app = FastAPI(
    title="ComicCraft API",
    description="AI Comic Story Creator using Gemini and image generation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.include_router(router)
