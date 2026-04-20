from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Keycloak
    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_ADMIN_USERNAME: str
    KEYCLOAK_ADMIN_PASSWORD: str

    # Razorpay
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # SMS
    SMS_API_KEY: str = "YOUR_API_KEY"
    SMS_FLOW_ID: str = "YOUR_FLOW_ID"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()