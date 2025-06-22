# main.py - примерная структура (ты пишешь сам!)

from aiogram import Bot, Dispatcher
import asyncio

from app.config import settings
from app.container import Container
from app.bot.middlewares.user_middleware import UserMiddleware

async def main() -> None:
    # 1. Создаем контейнер
    container = Container()
    
    # 2. Bot + Dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN.get_secret_value())
    dp = Dispatcher()
    
    # 3. Middleware
    dp.message.middleware(UserMiddleware(container.user_service))
    
    # 4. Services в DI
    dp["message_service"] = container.message_service
    dp["conversation_ai"] = container.conversation_ai
    
    # 5. Роутеры (тут решаем как именно)
    from app.bot.handlers.commands import router as commands_router
    dp.include_router(commands_router)
    
    # 6. Поехали!
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())