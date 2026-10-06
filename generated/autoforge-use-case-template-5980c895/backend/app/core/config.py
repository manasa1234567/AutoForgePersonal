from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "autoforge-use-case-template"
    PROJECT_VERSION: str = "1.0.0"

    # API
    API_V1_STR: str = "/api/v1"

    # DB
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "autoforge"

    # Database URL
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Auth config
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:3000"]

    class Config:
        env_file = f"{Path(__file__).parent.parent.parent}/.env"

settings = Settings()
