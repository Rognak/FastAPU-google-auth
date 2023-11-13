from models import Book
from contracts import CreateBookSchema
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete


async def get_all(db: AsyncSession, limit: int = 100, skip: int = 0) -> List[Book]:
    query = select(Book).limit(limit).offset(skip)
    res = await db.execute(query)
    return res.scalars().all()


async def get_by_id(db: AsyncSession, id: int) -> Optional[Book]:
    query = select(Book).where(Book.id == id).limit(1)
    res = await db.execute(query)
    return res.scalars().first()


async def create(db: AsyncSession, book_schema: CreateBookSchema) -> Book:
    book = Book(
        title=book_schema.title,
        description=book_schema.description,
        author=book_schema.author
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def update(db: AsyncSession, book: Book) -> Book:
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(db: AsyncSession, id: int) -> int:
    query = delete(Book).where(Book.id == id).returning(Book.id)
    res = await db.execute(query)
    await db.commit()
    return res.scalars().first()
