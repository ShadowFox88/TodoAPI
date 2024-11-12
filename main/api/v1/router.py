from fastapi import APIRouter

from main.api.v1.routes import user

router: APIRouter = APIRouter()

router.include_router(user.router, prefix="/users", tags=["user"])
