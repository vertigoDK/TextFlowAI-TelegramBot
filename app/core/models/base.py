from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData, DateTime
from sqlalchemy.sql import func
from datetime import datetime

metadata = MetaData(naming_convention={
    "pk": "pk_%(table_name)s"
})

class Base(DeclarativeBase):
    metadata = metadata

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
