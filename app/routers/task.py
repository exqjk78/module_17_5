from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify
from sqlalchemy.orm import Session


router = APIRouter(prefix='/task', tags=['task'])

@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    get_all_tasks = db.scalars(select(Task).where(Task.is_active == True)).all()
    return get_all_tasks

@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    get_task = db.scalar(select(Task).where(Task.id == task_id))
    if get_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no task found')
    return get_task

@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, create_task: CreateTask):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404,
                            detail="User was not found")

    db.execute(insert(Task).values(title=create_task.title,
                                   content=create_task.content,
                                   priority=create_task.priority,
                                   slug=slugify(create_task.title),
                                   user_id=user_id))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'}

@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, update_task: UpdateTask):
    updatetask = db.scalar(select(Task).where(Task.id == task_id))
    if updatetask is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no task found')

    db.execute(update(Task).where(Task.id == task_id).values(title=update_task.title,
                                                             content=update_task.content,
                                                             priority=update_task.priority,
                                                             slug=slugify(update_task.title)))
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'Task update is successful'}

@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    deletetask = db.scalar(select(Task).where(Task.id == task_id))
    if deletetask is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no task found')
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'Task delete is successful'}