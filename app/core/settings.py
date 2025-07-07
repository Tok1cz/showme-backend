from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    base_image_url: str = "http://localhost:8000/images/"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() # type: ignore
