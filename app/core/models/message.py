from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.types import Enum as EnumType
from typing import Optional


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Message(Base):
    __tablename__ = "messages"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[MessageRole] = mapped_column(EnumType(MessageRole))
    status: Mapped[MessageStatus] = mapped_column(
        EnumType(MessageStatus), default=MessageStatus.PENDING
    )
    content: Mapped[str] = mapped_column(String(1000))
    ai_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
