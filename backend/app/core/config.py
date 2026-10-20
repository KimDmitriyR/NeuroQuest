from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://neuroquest:neuroquest@127.0.0.1:5432/neuroquest"
    cors_allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    # dev-only default - MUST be overridden via .env in any real deployment
    jwt_secret_key: str = "dev-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 30  # 30 days - parents stay logged in
    # a child's device keeps playing for months without a parent logging in
    player_token_expire_days: int = 180

    # login brute-force protection (failed attempts per window, per process)
    login_rate_limit_window_seconds: int = 15 * 60
    login_max_failures_per_ip_email: int = 5
    login_max_failures_per_ip: int = 20
    login_max_failures_per_email: int = 30


settings = Settings()
