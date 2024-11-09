from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def return_logged_in_user():
    return {"username": "fakeuser"}