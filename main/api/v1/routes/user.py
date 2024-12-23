"""Module containing the routes for the users API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from main.core.database import get_session
from main.core.schema.token import TokenBase, TokenCreate, Tokens
from main.core.schema.user import UserCreate, UserRead, Users
from main.core.settings import AppSettings
from main.utils.errors import invalid_token, unauthorised
from main.utils.user_authentication import hash_password, verify_password
from passlib import pwd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

router = APIRouter()

settings = AppSettings()

get_bearer_token = HTTPBearer()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CredentialDep = Annotated[HTTPAuthorizationCredentials, Depends(get_bearer_token)]

async def get_logged_in_details(
    credentials: CredentialDep,
    session: AsyncSession = None,
) -> Users | None:
    """
    Return the logged in user and their token.
    """
    if session is None:
        session = Depends(get_session)
    result = await session.scalars(
        select(Tokens).where(Tokens.token == credentials.credentials),
    )
    token = result.first()

    if not token:
        raise unauthorised

    authenticated_token = token if token.token == credentials.credentials else None

    if authenticated_token is None:
        raise invalid_token

    if not authenticated_token.active:
        raise invalid_token

    if datetime.now(tz=timezone.utc) > authenticated_token.expires_at:
        raise invalid_token

    result = await session.scalars(
        select(Users).where(Users.id == authenticated_token.user_id),
    )

    users = result.all()

    authenticated_user = users[0] if users else None

    return {"User": authenticated_user, "Token": authenticated_token}

UserDep = Annotated[Users, Depends(get_logged_in_details)]

@router.get("/")
async def return_logged_in_user(
    logged_in_details: UserDep,
) -> UserRead:
    """
    Return the logged in user.
    """
    return logged_in_details["User"]


@router.post("/")
async def create_user(
    user: UserCreate, session: AsyncSession = None
) -> UserRead:
    """
    Create a user.
    """
    if session is None:
        session = Depends(get_session)
    if len(user.username) > settings.USERNAME_MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be less than {settings.USERNAME_MAX_LENGTH} characters long.", # noqa: E501
        )

    hashed_password = hash_password(user.password)

    user_to_create = Users(username=user.username, hashed_password=hashed_password)

    try:
        session.add(user_to_create)
        await session.commit()
        await session.refresh(user_to_create)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        ) from None

    return user_to_create


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    logged_in_details: UserDep,
    session: AsyncSession = None,
):
    """
    Delete the logged in user.
    """
    if session is None:
        session = Depends(get_session)
    current_user = logged_in_details["User"]

    tokens = await session.execute(
        select(Tokens).where(Tokens.user_id == current_user.id),
    )

    tokens = tokens.scalars().all()

    for i in tokens:
        i.active = False
        await session.delete(i)

    await session.commit()


@router.post("/token")
async def generate_token(
    token: TokenCreate,
    session: AsyncSession = None,
) -> TokenBase:
    """
    Generate a new token for the logged in user.
    """
    if session is None:
        session = Depends(get_session)

    result = await session.scalars(
        select(Users).where(Users.username == token.username),
    )
    user = result.first()

    authenticated_user: Users | None = None

    if not user:
        raise unauthorised

    if verify_password(token.password, user.hashed_password):
        raise unauthorised

    authenticated_user = user

    expires = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.AUTH_TOKEN_EXPIRATION
    )

    encoded_token = str(pwd.genword(entropy=512))

    created_token = Tokens(
        token=encoded_token,
        token_type="bearer",  # noqa: S106
        expires_at=expires,
        user_id=authenticated_user.id,
    )

    tokens = await session.execute(
        select(Tokens).where(Tokens.user_id == authenticated_user.id),
    )
    tokens = tokens.scalars().all()

    session.add(created_token)
    await session.commit()
    await session.refresh(created_token)

    return created_token


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: UserDep,
    session: AsyncSession = None,
):
    """
    Logout the logged in user.

    This will invalidate the current token.
    """
    if session is None:
        session = Depends(get_session)

    current_token = current_user["Token"]

    current_token.active = False
    session.add(current_token)

    await session.commit()


@router.post("/logout/all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    current_user: UserDep,
    session: AsyncSession = None,
):
    """
    Logout the logged in user from all devices.

    This invalidates all the user's tokens.
    """
    if session is None:
        session = Depends(get_session)

    tokens = await session.execute(
        select(Tokens).where(Tokens.user_id == current_user["User"].id),
    )
    tokens = tokens.scalars().all()

    for i in tokens:
        i.active = False
        session.add(i)

    await session.commit()
