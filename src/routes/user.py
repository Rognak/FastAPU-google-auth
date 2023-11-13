from fastapi import APIRouter, Depends, HTTPException, status
from contracts import UserSchema, UserRegisterSchema, UserUpdateSchema
from dependencies import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from queries import user as user_queries
from models import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def read_users(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    skip: int = 0) -> list[UserSchema]:
    return await user_queries.get_all(db=db, limit=limit, skip=skip)


@router.post("")
async def create_user(user: UserRegisterSchema, db: AsyncSession = Depends(get_db)) -> UserSchema:
    user = await user_queries.create(db=db, user_schema=user)
    user_schema = UserSchema(username=user.username, email=user.email, full_name=user.full_name)
    return user_schema


@router.put("")
async def update_user(
    id: int,
    user: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)) -> UserSchema:

    old_user = await user_queries.get_by_id(db=db, id=id)

    if old_user is None or old_user.email != current_user.email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    old_user.username = user.username if user.username is not None else old_user.username
    old_user.email = user.email if user.email is not None else old_user.email
    old_user.full_name = user.full_name if user.full_name is not None else old_user.full_name

    new_user = await user_queries.update(db=db, user=old_user)

    return UserSchema.from_orm(new_user)