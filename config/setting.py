# config/settings.py
import os
from typing import Dict, Any
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """Load application configuration from environment variables"""
    load_dotenv()
    
    return {
        # AI Configuration
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        
        # Database Configuration
        "database_url": os.getenv("DATABASE_URL", "sqlite:///./data/support_coordinator.db"),
        
        # Application Settings
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "secret_key": os.getenv("SECRET_KEY", "dev-secret-key"),
        "max_concurrent_users": int(os.getenv("MAX_CONCURRENT_USERS", "50")),
        "document_generation_timeout": int(os.getenv("DOCUMENT_GENERATION_TIMEOUT", "45")),
        
        # File Settings
        "max_file_size": int(os.getenv("MAX_FILE_SIZE", "52428800")),  # 50MB
        "allowed_extensions": ["pdf", "docx", "txt"],
        
        # Credit System
        "credits_per_generation": int(os.getenv("CREDITS_PER_GENERATION", "10")),
        "credits_per_edit": int(os.getenv("CREDITS_PER_EDIT", "5")),
        "default_credits": int(os.getenv("DEFAULT_CREDITS", "100")),
        
        # Paths
        "template_dir": "./templates/ndis_reports",
        "upload_dir": "./uploads/client_documents",
        "output_dir": "./output/generated",
        "temp_dir": "./output/temp"
    }