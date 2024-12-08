from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel  # type: ignore


class Tokens(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field()
    active: bool = Field(default=True)
    token: str = Field()
    token_type: str = Field()


class TokenBase(SQLModel):
    token: str = Field()
    token_type: str = Field()
    active: bool = Field(default=True)


class TokenCreate(SQLModel):
    username: str
    password: str