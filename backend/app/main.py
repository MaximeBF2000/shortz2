"""FastAPI application: python -m uvicorn app.main:app"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import storage
from app.api import brand_kits, catalog, clips, projects
from app.config import get_settings
from app.db import create_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Shortz API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for module in (projects, clips, brand_kits, catalog):
        app.include_router(module.router)

    storage.data_dir().mkdir(parents=True, exist_ok=True)
    settings.fonts_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=storage.data_dir()), name="media")
    app.mount("/fonts", StaticFiles(directory=settings.fonts_dir), name="fonts")
    return app


app = create_app()
