from sqlalchemy import BigInteger, Integer, String
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[str] = mapped_column(String(64))
    daily_limit: Mapped[int] = mapped_column(Integer, default=20)
    requests_today: Mapped[int] = mapped_column(Integer, default=0)