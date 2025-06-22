from app.core.services.ai.providers.google_provider import GoogleProvider
from app.core.services.ai.generator import AIGenerator
from app.core.services.ai.prompt_builders.conversation_prompt_builder import ConversationPromptBuilder
from app.core.services.ai.providers.google_provider import GoogleProvider


class Container:
    def __init__(self) -> None:
        # Создаем ОДИН РАЗ при старте приложения
        self._provider = GoogleProvider("gemini-2.0-flash")
        
        self._conversation_ai = AIGenerator(
            provider=self._provider,
            prompt_builder=ConversationPromptBuilder()
        )
        
        # self._translator_ai = AIGenerator(
        #     provider=self._provider,
        #     prompt_builder=TranslationPromptBuilder()
        # )
        
        # self._summarizer_ai = AIGenerator(
        #     provider=self._provider,
        #     prompt_builder=SummarizationPromptBuilder()
        # )
    
    @property
    def conversation_ai(self) -> AIGenerator:
        return self._conversation_ai
    
    # @property 
    # def translator_ai(self) -> AIGenerator:
    #     return self._translator_ai
    
    # @property
    # def summarizer_ai(self) -> AIGenerator:
    #     return self._summarizer_ai

