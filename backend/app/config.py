from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str
    mongodb_database: str
    # ...other settings...
    class Config:
        env_file = ".env"
