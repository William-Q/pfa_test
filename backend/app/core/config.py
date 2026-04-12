"""Centralized settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration object."""

    project_name: str = "PennyWise"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://pennywise_user:change_me@db:5432/pennywise"
    backend_cors_origins: str = "http://localhost:8501"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
