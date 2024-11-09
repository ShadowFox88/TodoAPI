from main.core.settings import AppSettings as settings
from fastapi.middleware.cors import CORSMiddleware
from main.api.v1.router import router as main_api_router

from fastapi import FastAPI

def create_app() -> FastAPI:
    """
    Creates the FastAPI application
    """
    
    app: FastAPI = FastAPI()
    
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
