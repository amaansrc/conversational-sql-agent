from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.config.settings import settings


class LLMService:

    @staticmethod
    def get_llm():
        provider = settings.LLM_PROVIDER.lower()

        if provider == "groq":
            return ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.MODEL_NAME,
                temperature=0
            )

        if provider == "openai":
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.MODEL_NAME,
                temperature=0
            )

        raise ValueError(f"Unsupported provider: {provider}")
