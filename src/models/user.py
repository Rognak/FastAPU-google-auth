from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa
from models import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(sa.String, unique=True)
    email: Mapped[str] = mapped_column(sa.String, unique=True)
    full_name: Mapped[str] = mapped_column(sa.String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(sa.String, nullable=True)
