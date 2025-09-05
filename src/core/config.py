import os
from dotenv import load_dotenv

load_dotenv()

# Application Settings
class Settings:
    # API Configuration
    cohere_api_key: str = os.getenv("COHERE_API_KEY")
    model_name: str = "command-a-03-2025"
    
    app_title: str = "Cohere Chat API"
    app_version: str = "1.0.0"
    history_file: str = "chat_history.json"
    
    def validate(self):
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

settings = Settings()