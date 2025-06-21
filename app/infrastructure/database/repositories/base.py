from typing import Any, TypeVar, Generic, Type, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    
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
        await self.session.refresh(model)

        return model

    async def update(self, id: int, **kwargs: Any) -> Optional[ModelType]:
        
        instance: Optional[ModelType] = await self.get_by_id(id)

        if instance is None:
            return None

        for key, value in kwargs.items():
            setattr(instance, key, value)
        
        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def delete(self, id: int) -> bool:
        
        instance: Optional[ModelType] = await self.get_by_id(id)

        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.commit()

        return True