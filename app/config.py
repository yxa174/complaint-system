from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./complaints.db"
    sentiment_api_key: str
    openai_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    
    class Config:
        env_file = ".env"

settings = Settings()
