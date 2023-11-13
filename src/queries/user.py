from models import User
from contracts import UserRegisterSchema, UserSchema
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.utils import PasswordUtils


async def get_all(db: AsyncSession, limit: int = 100, skip: int = 0) -> List[User]:
    query = select(User).limit(limit).offset(skip)
    res = await db.execute(query)
    return res.scalars().all()


async def get_by_id(db: AsyncSession, id: int) -> Optional[User]:
    query = select(User).where(User.id == id).limit(1)
    res = await db.execute(query)
    return res.scalars().first()


async def create(db: AsyncSession, user_schema: UserRegisterSchema | UserSchema) -> User:

    if isinstance(user_schema, UserSchema):
        user = User(
            username=user_schema.username,
            email=user_schema.email,
            full_name=user_schema.full_name,
        )
    else:
        user = User(
            username=user_schema.username,
            email=user_schema.email,
            full_name=user_schema.full_name,
            hashed_password=PasswordUtils.hash_password(user_schema.password),
        )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_by_email(db: AsyncSession, email: str) -> User:
    query = select(User).where(User.email == email).limit(1)
    res = await db.execute(query)
    user = res.scalars().first()
    return user
