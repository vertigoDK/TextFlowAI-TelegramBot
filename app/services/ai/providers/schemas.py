from typing import Any
from pydantic import BaseModel, Field, SecretStr, field_validator
from google.genai.types import GenerateContentConfig

class BaseProviderConfig(BaseModel):
    api_key: SecretStr = Field(...)
    model_name: str = Field(...)

class GoogleProviderConfig(BaseProviderConfig):
    generate_content_config: GenerateContentConfig = Field(...)

    @field_validator("model_name")
    @classmethod
    def check_model_name(cls, v: Any) -> Any:
        if v not in ['gemini-2.0-flash', 'gemini-2.5-flash']:
            raise ValueError("Invalid model name")
        return v

class OpenAIProviderConfig(BaseProviderConfig):
    ...
