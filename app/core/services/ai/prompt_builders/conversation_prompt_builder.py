from typing import List
from app.core.models.message import Message


class ConversationPromptBuilder:

    def build(self, messages: List[Message]) -> str:

        system_prompt = "You are a helpful assistant."

        formated_messages = "\n".join(
            [f"{message.role}: {message.content}" for message in messages]
        )
        return system_prompt + "\n\n" + formated_messages
