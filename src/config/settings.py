# src/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # GitHub settings
    github_token: str
    repository_name: str
    
    # OpenAI settings
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    
    # Application settings
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Делаем нечувствительным к регистру

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Удаляем возможные пробелы в значениях
        self.github_token = self.github_token.strip()
        self.repository_name = self.repository_name.strip()
        self.openai_api_key = self.openai_api_key.strip()