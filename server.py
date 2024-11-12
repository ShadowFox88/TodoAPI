from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel

from main.api.v1.router import router as main_api_router
from main.core.settings import AppSettings

settings = AppSettings()


class CustomApp(FastAPI):
    def __init__(self, *args: Any, **kwargs: Dict[str, Any]):
        super().__init__(*args, **kwargs)

    @staticmethod
    def return_engine() -> AsyncEngine:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
        )

        return engine

    async def startup(self):
        self.engine = self.return_engine()

        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def shutdown(self):
        await self.engine.dispose()


@asynccontextmanager
async def lifespan(app: CustomApp):
    await app.startup()

    yield

    await app.shutdown()


def create_app() -> CustomApp:
    """
    Creates the FastAPI application
    """

    app: CustomApp = CustomApp(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for i in settings.ALL_API_VERSIONS:
        if i not in settings.DEPRECATED_API_VERSIONS:
            app.include_router(main_api_router, prefix=f"/{settings.API_PREFIX}/{i}")

    return app


app = create_app()
