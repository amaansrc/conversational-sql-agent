from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure SQL Database connection settings
    AZURE_SQL_SERVER: str = ""
    AZURE_SQL_DATABASE: str = ""
    AZURE_SQL_USERNAME: str = ""
    AZURE_SQL_PASSWORD: str = ""
    AZURE_SQL_DRIVER: str = "{ODBC Driver 18 for SQL Server}"

    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    MODEL_NAME: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self) -> str:
        """Build the SQLAlchemy connection string for Azure SQL Database."""
        from urllib.parse import quote_plus

        params = quote_plus(
            f"DRIVER={self.AZURE_SQL_DRIVER};"
            f"SERVER=tcp:{self.AZURE_SQL_SERVER},1433;"
            f"DATABASE={self.AZURE_SQL_DATABASE};"
            f"UID={self.AZURE_SQL_USERNAME};"
            f"PWD={self.AZURE_SQL_PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        return f"mssql+pyodbc:///?odbc_connect={params}"


@lru_cache

def get_settings():
    return Settings()


settings = get_settings()
