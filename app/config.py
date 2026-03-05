import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    VERSION: str = os.getenv("VERSION", "0.1.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    SERVICE_NAME: str = "cryptocurrency"

    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"

    class Config:
        env_file = ".env"


settings = Settings()
