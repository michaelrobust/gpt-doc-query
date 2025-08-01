import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "demo-key-for-github-showcase")
    
    
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    
   
    UPLOAD_DIR: str = "../data/uploads"
    VECTOR_DB_PATH: str = "../data/vector_db"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    class Config:
        env_file = "../.env"
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.DEMO_MODE:
            print("🎭 Running in DEMO MODE - no real API keys needed")
        elif not self.OPENAI_API_KEY or self.OPENAI_API_KEY == "demo-key-for-github-showcase":
            print("⚠️ Please set OPENAI_API_KEY in .env file for production use")

settings = Settings()