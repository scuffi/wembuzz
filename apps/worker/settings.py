from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = Field(..., env="MONGO_URI")
    mongo_db: str = Field(..., env="MONGO_DB")
    openrouter_key: str = Field(..., env="OPENROUTER_KEY")

    event_cutoff_days: int = Field(7, env="EVENT_CUTOFF_DAYS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
