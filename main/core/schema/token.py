"""Defines the schema for the token objects."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Tokens(SQLModel, table=True):
    """Table model for the token objects."""

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field()
    active: bool = Field(default=True)
    token: str = Field()
    token_type: str = Field()


class TokenBase(SQLModel):
    """Base model for the tokens objects."""

    token: str = Field()
    token_type: str = Field()
    active: bool = Field(default=True)


class TokenCreate(SQLModel):
    """Model used for creating a new token."""

    username: str
    password: str
