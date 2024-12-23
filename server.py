"""Main file to start the application."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main.api.v1.router import router as main_api_router
from main.core.settings import AppSettings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel

settings = AppSettings()


class CustomApp(FastAPI):
    """
    Custom FastAPI application class.

    This class is used to create the FastAPI application with a couple of useful functions.
    """ # noqa: E501

    def __init__(self, *args: any, **kwargs: dict[str, Any]) -> None:  # noqa: D107
        super().__init__(*args, **kwargs)

    @staticmethod
    def return_engine() -> AsyncEngine:  # noqa: D102
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
        )

    async def startup(self) -> None:  # noqa: D102
        self.engine = self.return_engine()

        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def shutdown(self) -> None:  # noqa: D102
        await self.engine.dispose()


@asynccontextmanager
async def lifespan(app: CustomApp) -> None:  # noqa: D103
    await app.startup()

    yield

    await app.shutdown()


def create_app() -> CustomApp:
    """Create the FastAPI application."""
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
