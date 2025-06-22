from app.core.services.ai.providers.google_provider import GoogleProvider
from app.core.services.ai.generator import AIGenerator
from app.core.services.ai.prompt_builders.conversation_prompt_builder import (
    ConversationPromptBuilder,
)
from app.core.services.ai.providers.google_provider import GoogleProvider


from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.message_repository import (
    MessageRepository,
)
from app.core.services.user_service import UserService
from app.core.services.message_service import MessageService


class Container:
    def __init__(self) -> None:
        # Создаем ОДИН РАЗ при старте приложения
        self._provider = GoogleProvider("gemini-2.0-flash")

        self._conversation_ai = AIGenerator(
            provider=self._provider, prompt_builder=ConversationPromptBuilder()
        )

    async def get_user_service(self):
        session = SessionLocal()
        user_repository = UserRepository(session)
        return UserService(user_repository)

    async def get_message_service(self):
        session = SessionLocal()
        user_repository = UserRepository(session)
        message_repository = MessageRepository(session)
        return MessageService(user_repository, message_repository)

    @property
    def conversation_ai(self) -> AIGenerator:
        return self._conversation_ai

    # @property
    # def translator_ai(self) -> AIGenerator:
    #     return self._translator_ai

    # @property
    # def summarizer_ai(self) -> AIGenerator:
    #     return self._summarizer_ai
