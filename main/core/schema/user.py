from sqlmodel import Field, SQLModel # type: ignore
from uuid import UUID, uuid4
from datetime import datetime

class Users(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default=uuid4)
    username: str = Field(max_length=16, unique=True)
    hashed_password: str = Field()
    salt: str = Field()
    created_at: datetime = Field(default=datetime.now)
    disabled: bool = Field(default=False)

class UserBase(SQLModel):
    username: str = Field(max_length=16)
    
class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID

