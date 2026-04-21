from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PROGRAM
    ENVIRONMENT: str

    # DB
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
