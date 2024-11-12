from sqlmodel import SQLModel, Field # type: ignore
from uuid import UUID, uuid4
from datetime import datetime

class TokenBase(SQLModel):
    token: str = Field()
    token_type: str = Field()    

class Tokens(TokenBase, table=True):
    id: UUID = Field(primary_key=True, default=uuid4)
    user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default=datetime.now)
    expires_at: datetime = Field()