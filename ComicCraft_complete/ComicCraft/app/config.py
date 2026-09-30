from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    hf_token: str | None = Field(default=None, alias="HF_TOKEN")

    gemini_outline_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_OUTLINE_MODEL")
    gemini_story_model: str = Field(default="gemini-2.5-pro", alias="GEMINI_STORY_MODEL")

    image_provider: str = Field(default="hf", alias="IMAGE_PROVIDER")
    hf_image_model: str = Field(default="black-forest-labs/FLUX.1-schnell", alias="HF_IMAGE_MODEL")
    local_image_model: str = Field(default="runwayml/stable-diffusion-v1-5", alias="LOCAL_IMAGE_MODEL")

    default_panels: int = Field(default=5, alias="DEFAULT_PANELS")
    max_panels: int = Field(default=8, alias="MAX_PANELS")

    base_dir: Path = Path(__file__).resolve().parent.parent
    templates_dir: Path = base_dir / "templates"
    static_dir: Path = base_dir / "static"
    panels_dir: Path = static_dir / "panels"
    exports_dir: Path = static_dir / "exports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    return settings
