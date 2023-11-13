from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from dependencies import get_db, get_current_user
from models import User
from queries import books as books_queries
from contracts import CreateBookSchema, BookSchema, UpdateBookSchema


router = APIRouter(prefix="/books", tags=["books"])


@router.get("")
async def read_books(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
) -> list[BookSchema]:

    return await books_queries.get_all(db=db, limit=limit, skip=skip)


@router.post("")
async def create_book(book: CreateBookSchema,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)) -> BookSchema:
    book = await books_queries.create(db=db, book_schema=book)
    return BookSchema.model_validate(book)


@router.put("")
async def update_book(
    id: int,
    book: UpdateBookSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)) -> BookSchema:

    old_book = await books_queries.get_by_id(db=db, id=id)

    if old_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    old_book.title = book.title if book.title is not None else old_book.title
    old_book.description = book.description if book.description is not None else old_book.description
    old_book.author = book.author if book.author is not None else old_book.author

    new_book = await books_queries.update(db=db, book=old_book)

    return BookSchema.model_validate(new_book)


@router.delete("")
async def delete(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> int:
    res = await books_queries.delete_book(db=db, id=id)
    return res
