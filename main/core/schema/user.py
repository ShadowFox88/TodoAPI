"""Defines the schema for the User objects."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Users(SQLModel, table=True):
    """Table model for the User objects."""

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    username: str = Field(max_length=16, unique=True)
    hashed_password: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    disabled: bool = Field(default=False)


class UserBase(SQLModel):
    """Base model for the User objects."""

    username: str = Field(max_length=16)


class UserCreate(UserBase):
    """Model used for creating a new user."""

    password: str


class UserRead(UserBase):
    """Model for returning a user object to the user."""

    id: UUID
    disabled: bool = Field(default=False)
