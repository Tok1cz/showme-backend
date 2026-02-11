from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    REGIONS: ClassVar[list[str]] = ["great-britain", "germany"]
    CONTINENT: ClassVar[str] = "europe"

    DATABASE_URL: str
    DATABASE_URL_SYNCH: str
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str
    BASE_IMAGE_URL: str = "http://localhost:8000/images/"
    DEBUG: bool = False
    OSM_BASE_URL: str = "https://download.geofabrik.de/"
    OSM_IMPORT_DIR: str = "/var/tmp/osm_imports/"
    OSM_RETENTION_DAYS: int = 2
    OPEN_API_KEY: str
    MEDIA_STORAGE_BACKEND: str = "local"

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    JWT_SECRET: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
