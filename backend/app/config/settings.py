from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///AdventureWorksLT.db"
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    MODEL_NAME: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"


@lru_cache

def get_settings():
    return Settings()


settings = get_settings()
