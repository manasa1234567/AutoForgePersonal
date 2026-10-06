from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "cld_user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "cld_db"
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    # Azure AD config (OpenID Connect)
    AZURE_AD_TENANT_ID: str | None = None
    AZURE_AD_CLIENT_ID: str | None = None
    AZURE_AD_ISSUER: str | None = None

    # Other settings can be added here...

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def assemble_db_connection(self):
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()
settings.SQLALCHEMY_DATABASE_URI = settings.assemble_db_connection()
