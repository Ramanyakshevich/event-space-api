from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EventSpace API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str
    SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @property
    def CELERY_BROKER_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
    @property
    def CELERY_RESULT_BACKEND(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()