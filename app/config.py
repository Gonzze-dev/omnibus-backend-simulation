from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/terminales"

    class Config:
        env_file = ".env"


settings = Settings()
