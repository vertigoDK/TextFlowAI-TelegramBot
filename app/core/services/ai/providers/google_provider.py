from typing import List, Any, Literal
from app.core.models.message import Message
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings


class GoogleProvider:

    def __init__(
        self,
        model_name: Literal['gemini-2.0-flash']
    ):
        self.llm = ChatGoogleGenerativeAI(
            api_key=settings.GOOGLE_API_KEY.get_secret_value(),
            model_name=model_name,
        )
        self.model_name = model_name

    async def agenerate(
        self,
        prompt: str
    ) -> dict[str, Any]:
        try:
            response = await self.llm.ainvoke(prompt)
            return {
                "content": response.content,
                "model": self.model_name,
                "usage": response.response_metadata,
            }
        except Exception as e:
            raise