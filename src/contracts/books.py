import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CreateBookSchema(BaseModel):
    title: str
    description: str
    author: str


class BookSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    author: str
    publish_date: datetime.datetime


class UpdateBookSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[bool] = None