from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_REALM: str

    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str

    KEYCLOAK_ADMIN_USERNAME: str
    KEYCLOAK_ADMIN_PASSWORD: str

    class Config:
        env_file = ".env"



    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # SMS (MSG91) #Later when implemented
    SMS_API_KEY: str = "YOUR_API_KEY"
    SMS_FLOW_ID: str = "YOUR_FLOW_ID"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

settings = Settings()
