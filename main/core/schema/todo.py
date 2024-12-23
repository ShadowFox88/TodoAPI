"""Defines the schema for the Todo tasks."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    """Table model for the Todo Tasks."""

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    owner_id: UUID = Field(foreign_key="users.id")
    title: str = Field(max_length=128)
    description: str = Field()
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    due_at: datetime = Field()


class TodoBase(SQLModel):
    """Base model for all tasks returned."""

    title: str = Field(max_length=128)
    description: str = Field()
    due_at: datetime = Field()


class TodoCreate(TodoBase):
    """Model for creating a new task."""

    id: UUID


class TodoRead(TodoBase):
    """Model for returning a task to the user."""

    id: UUID
    completed: bool = Field(default=False)
