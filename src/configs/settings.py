from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    DASHBOARDS_SERVICE_URL: str
    API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
