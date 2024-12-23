from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4

class Todo(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    owner_id: UUID = Field(foreign_key="users.id")
    title: str = Field(max_length=128)
    description: str = Field()
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    due_at: datetime = Field()
    
class TodoBase(SQLModel):
    title: str = Field(max_length=128)
    description: str = Field()
    due_at: datetime = Field()
    
class TodoCreate(TodoBase):
    id: UUID
    
class TodoRead(TodoBase):
    id: UUID
    completed: bool = Field(default=False)