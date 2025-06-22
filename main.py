# # main.py - примерная структура (ты пишешь сам!)

# from aiogram import Bot, Dispatcher
# import asyncio

# from app.config.settings import settings
# from app.core.services.container import Container
# from app.bot.middlewares.user_middleware import UserMiddleware

# async def main() -> None:
#     container = Container()
    
#     bot = Bot(token=settings.TELEGRAM_BOT_TOKEN.get_secret_value())
#     dp = Dispatcher()
    
#     dp.message.middleware(UserMiddleware(container.user_service))
    
#     dp["message_service"] = container.message_service
#     dp["conversation_ai"] = container.conversation_ai
    
#     from app.bot.handlers.commands import router as commands_router
#     dp.include_router(commands_router)
    
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())