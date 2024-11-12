from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel  # type: ignore


class Users(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    username: str = Field(max_length=16, unique=True)
    hashed_password: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    disabled: bool = Field(default=False)


class UserBase(SQLModel):
    username: str = Field(max_length=16)


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID
    disabled: bool = Field(default=False)
