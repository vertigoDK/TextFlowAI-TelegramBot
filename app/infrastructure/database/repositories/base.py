from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Type, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(ABC, Generic[ModelType]):
    
    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        self.session = session
        self.model = model_class

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        
        stmt = select(self.model).where(self.model.id == id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create(self, **kwargs: Any) -> ModelType:
        
        model = self.model(**kwargs)

        self.session.add(model)

        await self.session.commit()

        return model