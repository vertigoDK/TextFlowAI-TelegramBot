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

        # Создаем сессию для репозиториев
        self._session = SessionLocal()
        self._user_repository = UserRepository(self._session)
        self._message_repository = MessageRepository(self._session)
        self._user_service = UserService(self._user_repository)
        self._message_service = MessageService(
            self._user_repository, self._message_repository
        )

    @property
    def user_repository(self):
        return self._user_repository

    @property
    def message_repository(self):
        return self._message_repository

    @property
    def user_service(self):
        return self._user_service

    @property
    def message_service(self):
        return self._message_service

    @property
    def conversation_ai(self) -> AIGenerator:
        return self._conversation_ai

    # @property
    # def translator_ai(self) -> AIGenerator:
    #     return self._translator_ai

    # @property
    # def summarizer_ai(self) -> AIGenerator:
    #     return self._summarizer_ai
