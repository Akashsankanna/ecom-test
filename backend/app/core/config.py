from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # KEYCLOAK CONFIG
    # =========================
    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_ADMIN_USERNAME: str
    KEYCLOAK_ADMIN_PASSWORD: str

    # =========================
    # RAZORPAY CONFIG
    # =========================
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # =========================
    # REDIS CONFIG
    # =========================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # =========================
    # SMS CONFIG
    # =========================
    SMS_API_KEY: str = "YOUR_API_KEY"
    SMS_FLOW_ID: str = "YOUR_FLOW_ID"

    # =========================
    # PYDANTIC SETTINGS CONFIG
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()