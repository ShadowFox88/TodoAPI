import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Dict, List

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from passlib.hash import bcrypt
from passlib import pwd
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from main.core.database import get_session
from main.core.schema.token import TokenBase, TokenCreate, Tokens
from main.core.schema.user import UserCreate, UserRead, Users
from main.core.settings import AppSettings

router = APIRouter()

settings = AppSettings()

get_bearer_token = HTTPBearer()


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(get_bearer_token), session: AsyncSession = Depends(get_session)) -> Users | None:
    result = await session.execute(
        select(Tokens).where(Tokens.token == token.credentials)
    )
    
    tokens = result.scalars().all()
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if len(tokens) > 1:
        # This should never occur, and means I fucked up somewhere
        exit()
    
    authenticated_token = tokens[0] if tokens[0].token == token.credentials else None
    
    if authenticated_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not authenticated_token.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if datetime.now() > authenticated_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    result = await session.execute(
        select(Users).where(Users.id == authenticated_token.user_id)
    )
    
    users = result.scalars().all()
    
    authenticated_user = users[0] if users else None
    
    return authenticated_user
    
    
@router.get("/", response_model=UserRead)
async def return_logged_in_user(current_user: Annotated[Users, Depends(get_current_user)]):
    return current_user


@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):

    if len(user.username) > 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be less than 16 characters long.",
        )

    password = user.password.encode("utf-8")
    sha_password = base64.b64encode(hashlib.sha256(password).digest())

    hashed_password = bcrypt.hash(sha_password)

    user_to_create = Users(username=user.username, hashed_password=hashed_password)

    session.add(user_to_create)
    await session.commit()
    await session.refresh(user_to_create)

    return user_to_create

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: Annotated[Users, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    
    tokens = await session.execute(
        select(Tokens).where(Tokens.user_id == current_user.id)
    )
    
    tokens = tokens.scalars().all()
    
    for i in tokens:
        i.active = False
        await session.delete(i)
    
    await session.delete(current_user)
    await session.commit()

@router.post("/token", response_model=TokenBase)
async def generate_jwt_token(
    token: TokenCreate, session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(Users).where(Users.username == token.username)
    )
    users = result.scalars().all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    authenticated_user: Users | None = None

    password = token.password.encode("utf-8")
    sha_password = base64.b64encode(hashlib.sha256(password).digest())

    for i in users:
        if bcrypt.verify(sha_password, i.hashed_password):
            authenticated_user = i
            break

    if authenticated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data: Dict[str, Any] = {}

    expires = datetime.now() + timedelta(minutes=settings.AUTH_TOKEN_EXPIRATION)
    token_data: Dict[str, Any] = {
        "expires-at": expires.strftime("%Y/%m/%d %H:%M:%S"),
        "token-type": "bearer",
        "username": authenticated_user.username,
        "random_data": str(pwd.genword(entropy=128)), # type: ignore
    }
    data.update(token_data)

    encoded_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    created_token = Tokens(
        token=encoded_token,
        token_type="bearer",
        expires_at=expires,
        user_id=authenticated_user.id,
    )

    tokens = await session.execute(
        select(Tokens).where(Tokens.user_id == authenticated_user.id)
    )
    tokens = tokens.scalars().all()

    for i in tokens:
        i.active = False
        session.add(i)

    session.add(created_token)
    await session.commit()
    await session.refresh(created_token)

    return created_token