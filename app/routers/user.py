from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify
from sqlalchemy.orm import Session


router = APIRouter(prefix='/user', tags=['user'])

@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    get_all_users = db.scalars(select(User).where(User.is_active == True)).all()
    return get_all_users

@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    get_user = db.scalar(select(User).where(User.id == user_id))
    if get_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no user found')
    return get_user

@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   first_name=create_user.firstname,
                                   last_name=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'}

@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, update_user: UpdateUser):
    updateuser = db.scalar(select(User).where(User.id == user_id))
    if updateuser is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no user found')

    db.execute(update(User).where(User.id == user_id).values(firstname=update_user.firstname,
                                                             lastname=update_user.lastname,
                                                             age=update_user.age))
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'User update is successful'}


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    deleteuser = db.scalar(select(User).where(User.id == user_id))
    if deleteuser is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no user found')
    db.execute(delete(User).where(User.id == user_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'User delete is successful'}


@router.get("/user/{user_id}/tasks")
def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    if tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no user found')
    return tasks


@router.delete("/delete/{user_id}")
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.scalar(select(User).where(User.id == user_id))

    if existing_user is None:
        raise HTTPException(status_code=404,
                            detail="User was not found")

    db.execute(delete(Task).where(Task.user_id == user_id))
    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    return {"status_code": status.HTTP_200_OK,
            "transaction": "User and associated tasks deleted successfully!"}