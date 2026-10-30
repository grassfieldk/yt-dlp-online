from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Required — no default; the app will refuse to start if unset
    api_key: str

    # Directory used for temporary download files
    temp_dir: str = "/tmp"

    # Default video height cap in pixels (1080 / 720 / 480 / 0 for best available)
    default_quality: int = 1080

    # Optional yt-dlp zipapp path shared with the command-line installation
    yt_dlp_path: str | None = None


settings = Settings()
