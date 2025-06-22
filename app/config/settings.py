from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    DATABASE_URL: SecretStr
    GOOGLE_API_KEY: SecretStr
    TELEGRAM_BOT_TOKEN: SecretStr


settings = Config()  # type: ignore
