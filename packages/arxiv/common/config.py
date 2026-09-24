from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./research_graph.db"
    arxiv_rate_limit_delay: float = 3.0
    semantic_scholar_api_key: str | None = None
    max_concurrent_downloads: int = 1

    class Config:
        env_file = ".env"

settings = Settings()
