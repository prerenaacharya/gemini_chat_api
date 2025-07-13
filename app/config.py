from pydantic_settings import BaseSettings  # ✅ Correct for v2

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_URL: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    GEMINI_API_KEY: str
    STRIPE_PRO_PRICE_ID: str

    class Config:
        env_file = ".env"

settings = Settings() # type: ignore
