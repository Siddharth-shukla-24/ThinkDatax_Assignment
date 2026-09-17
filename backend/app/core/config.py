from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    cors_origins: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/thinkdatax"
    api_token: str = "dev-local-token"
    app_secret: str = "dev-local-app-secret"
    app_base_url: str = "http://localhost:8000"
    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"
    sender_name: str = "Alex Rivera"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()