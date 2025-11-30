from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Ground Data API Gateway"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "ground"
    DB_PASSWORD: str = "ground"
    DB_NAME: str = "ground"

    class Config:
        env_file = ".env"


settings = Settings()
