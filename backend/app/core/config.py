from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    ollama_url: str = "http://localhost:11434/api/generate"

    ollama_model: str = "qwen2.5:3b-instruct"

    ollama_embedding_url: str = "http://localhost:11434/api/embed"

    ollama_embedding_model: str = "nomic-embed-text"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    documents_dir: Path = PROJECT_ROOT / "backend" / "data" / "documents"

    vector_store_dir: Path = PROJECT_ROOT / "backend" / "data" / "vector_store"

    max_upload_size_bytes: int = 20 * 1024 * 1024

settings = Settings()
