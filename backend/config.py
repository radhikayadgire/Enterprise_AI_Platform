"""Central configuration for the Enterprise AI Platform backend.

Values are sourced from environment variables (see .env) so behaviour can be
tuned per-deployment without code changes.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SECRET_KEY: str = "dev-secret-key-change-me"
    ALGORITHM: str = "HS256"

    # IMS-4: this value is MINUTES, not seconds. A prior build multiplied it
    # against timedelta(seconds=...) which turned "10 minutes" into a
    # 10-second-lived token - mobile clients hit that expiry almost
    # immediately after login and appeared to be "logged out after 10
    # seconds". Keep this in minutes and always build tokens with
    # timedelta(minutes=SESSION_TIMEOUT_MINUTES).
    SESSION_TIMEOUT_MINUTES: int = 30

    # Refresh tokens live much longer so a mobile app can silently renew the
    # access token instead of forcing a fresh login every 30 minutes.
    REFRESH_TOKEN_TIMEOUT_DAYS: int = 7

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_ADDRESS: str = "no-reply@enterprise-ai-platform.local"


settings = Settings()
