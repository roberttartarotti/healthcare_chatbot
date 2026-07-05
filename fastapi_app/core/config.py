"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from the environment and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Healthcare Assistant (hobby project)"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Return the configured CORS origins parsed into a list."""
        if not self.CORS_ORIGINS:
            return ["http://localhost:5173", "http://localhost:3000"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
