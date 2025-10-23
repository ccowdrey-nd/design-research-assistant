"""
Configuration management for the design assistant chatbot.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str
    figma_access_token: str
    
    # Figma Configuration
    figma_team_id: Optional[str] = None
    figma_file_keys: Optional[str] = None  # Comma-separated list of file keys
    
    # Google Configuration
    google_application_credentials: Optional[str] = None
    google_drive_folder_id: Optional[str] = None
    
    # Okta Configuration (optional for development)
    okta_domain: Optional[str] = None
    okta_client_id: Optional[str] = None
    okta_client_secret: Optional[str] = None
    okta_issuer: Optional[str] = None
    okta_redirect_uri: str = "http://localhost:3000/callback"
    skip_auth: bool = False  # Set to True to skip authentication in development
    
    # Application Settings
    app_name: str = "Design Assistant"
    debug: bool = False
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Database Settings
    chroma_persist_directory: str = "./data/chromadb"
    
    # OpenAI Settings
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4-turbo-preview"
    vision_model: str = "gpt-4-vision-preview"
    max_tokens: int = 1024  # Reduced for faster, more concise responses
    temperature: float = 0.7
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 3  # Reduced from 5 for faster responses
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

