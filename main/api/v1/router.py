"""
Import all the routes for the branches of the api.

API version 1.
"""

from fastapi import APIRouter

from main.api.v1.routes import todo, user

router: APIRouter = APIRouter()

router.include_router(user.router, prefix="/users", tags=["user"])
router.include_router(todo.router, prefix="/todos", tags=["todo"])
