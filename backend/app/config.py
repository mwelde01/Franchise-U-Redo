from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = "sqlite:///./podcast_db.sqlite"

    # Anthropic API (optional - AI features disabled if not set)
    ANTHROPIC_API_KEY: str = ""

    # File Storage
    AUDIO_STORAGE_PATH: str = "./audio_files"
    MAX_UPLOAD_SIZE: int = 500  # MB

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Preset Tags
    PRESET_TAGS: str = "technology,business,health,education,entertainment,science,sports,politics,culture,interviews,news,comedy,true-crime,history,self-improvement"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def preset_tags_list(self) -> List[str]:
        """Get preset tags as a list"""
        return [tag.strip() for tag in self.PRESET_TAGS.split(',')]

    def ensure_storage_dirs(self):
        """Create storage directories if they don't exist"""
        os.makedirs(self.AUDIO_STORAGE_PATH, exist_ok=True)
        os.makedirs(os.path.join(self.AUDIO_STORAGE_PATH, 'temp'), exist_ok=True)


settings = Settings()
settings.ensure_storage_dirs()
