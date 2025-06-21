from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.user import User
from .base import BaseRepository
from typing import Optional, Sequence
from sqlalchemy import select, update


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_user(
        self, telegram_id: int, first_name: str, username: Optional[str] = None
    ) -> User:

        user = await self.get_by_telegram_id(telegram_id)

        if user is None:
            user = await self.create(
                telegram_id=telegram_id, first_name=first_name, username=username
            )

        return user

    async def update_user_info(
        self, telegram_id: int, first_name: str, username: Optional[str] = None
    ) -> Optional[User]:

        user = await self.get_by_telegram_id(telegram_id)

        if not user:
            return None

        user = await self.update(user.id, first_name=first_name, username=username)

        return user

    async def increment_requests_today(self, telegram_id: int) -> bool:

        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(requests_today=User.requests_today + 1)
        )

        await self.session.execute(stmt)
        await self.session.commit()

        return True

    async def reset_daily_limits(self) -> int:
        stmt = select(User).where(User.requests_today > 0)

        users: Sequence[User] = (await self.session.execute(stmt)).scalars().all()

        for user in users:
            await self.update(user.id, requests_today=0)

        return len(users)
