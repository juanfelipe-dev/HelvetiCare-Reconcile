from pydantic import BaseSettings


class Settings(BaseSettings):
    max_upload_size_mb: int = 10
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()