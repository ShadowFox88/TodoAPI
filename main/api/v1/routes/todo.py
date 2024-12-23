from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from main.api.v1.routes.user import get_logged_in_details
from main.core.database import get_session
from main.core.schema.todo import Todo, TodoBase, TodoCreate, TodoRead
from main.core.schema.user import Users
from sqlalchemy.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.post("/", response_model=TodoCreate)
async def create_task(
    task: TodoBase,
    logged_in_details: Annotated[Users, Depends(get_logged_in_details)],
    session: AsyncSession = Depends(get_session),
):
    todo = Todo(**task.dict())
    todo.due_at = todo.due_at.replace(tzinfo=None)
    todo.created_at = todo.created_at.replace(tzinfo=None)
    todo.owner_id = logged_in_details["User"].id
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


@router.delete("/{todo_id}")
async def delete_task(
    todo_id: UUID,
    logged_in_details: Annotated[Users, Depends(get_logged_in_details)],
    session: AsyncSession = Depends(get_session),
):
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    if todo.owner_id != logged_in_details["User"].id:
        raise HTTPException(
            status_code=403, detail="Not authorised to delete this task"
        )
    await session.delete(todo)
    await session.commit()
    return {"message": "Todo deleted successfully"}


@router.get("/{todo_id}", response_model=TodoRead)
async def get_task(
    todo_id: UUID,
    logged_in_details: Annotated[Users, Depends(get_logged_in_details)],
    session: AsyncSession = Depends(get_session),
):
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    if todo.owner_id != logged_in_details["User"].id:
        raise HTTPException(status_code=403, detail="Not authorised to view this task")
    return todo
