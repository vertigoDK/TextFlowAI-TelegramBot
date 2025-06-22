from pydantic import SecretStr, ConfigDict
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    DATABASE_URL: SecretStr
    GOOGLE_API_KEY: SecretStr
    TELEGRAM_BOT_TOKEN: SecretStr


settings = Config()  # type: ignore
