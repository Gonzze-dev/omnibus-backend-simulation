from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "omnibus-terminal"
    DB_PORT: int = 5432
    DB_SSLMODE: str = "disable"
    # Orígenes separados por coma. Vacío = se permiten todos.
    CORS_ALLOWED_ORIGINS: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_URL}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"
        )

    @property
    def CORS_ORIGINS(self) -> list[str]:
        origins = [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
        return origins or ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
