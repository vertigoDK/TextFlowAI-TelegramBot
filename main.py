from aiogram import Bot, Dispatcher
import asyncio

from app.config.settings import settings
from app.core.services.container import Container
from app.bot.middlewares.user_middleware import UserMiddleware
from app.core.services.user_service import UserService
from app.core.services.message_service import MessageService


async def main() -> None:
    container = Container()

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN.get_secret_value())
    dp = Dispatcher()

    # Передаем контейнер в middleware
    dp.message.middleware(UserMiddleware(container))

    # Передаем контейнер в handlers
    dp["container"] = container

    from app.bot.handlers.commands import router as commands_router
    from app.bot.handlers.messages import router as messages_router

    dp.include_router(commands_router)
    dp.include_router(messages_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
