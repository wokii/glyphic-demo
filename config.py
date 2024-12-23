from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")
    claude_api_key: SecretStr


settings = Settings()
