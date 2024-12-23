"""Module containing the routes for the todo API."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from main.api.v1.routes.user import get_logged_in_details
from main.core.database import get_session
from main.core.schema.todo import Todo, TodoBase, TodoCreate, TodoRead
from main.core.schema.user import Users
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/")
async def create_task(
    task: TodoBase,
    logged_in_details: Annotated[Users, Depends(get_logged_in_details)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TodoCreate:
    """Create a new task."""
    todo = Todo(**task.dict())
    todo.due_at = todo.due_at.replace(tzinfo=None)
    todo.created_at = todo.created_at.replace(tzinfo=None)
    todo.owner_id = logged_in_details["User"].id
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    todo_id: UUID,
    logged_in_details: Annotated[Users, Depends(get_logged_in_details)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """
    Delete a task with the given ID.
    """
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    if todo.owner_id != logged_in_details["User"].id:
        raise HTTPException(
            status_code=403, detail="Not authorised to delete this task"
        )
    await session.delete(todo)
    await session.commit()


@router.get("/{todo_id}")
async def get_task(
    todo_id: UUID,
    logged_in_details: Annotated[Users, Depends(get_logged_in_details)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TodoRead:
    """
    Return a task with the given ID.
    """
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    if todo.owner_id != logged_in_details["User"].id:
        raise HTTPException(status_code=403, detail="Not authorised to view this task")
    return todo
