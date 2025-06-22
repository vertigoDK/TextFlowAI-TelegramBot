from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DATABASE_URL: SecretStr
    GOOGLE_API_KEY: SecretStr


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Config()  # type: ignore
