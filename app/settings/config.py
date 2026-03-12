import os
import typing

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    VERSION: str = "1.0.0"
    APP_TITLE: str = "AI 模拟面试系统"
    PROJECT_NAME: str = "AI 模拟面试系统"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = True

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")

    SECRET_KEY: str = Field(
        default="please-set-secret-key-in-env",
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET_KEY"),
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day

    DB_HOST: str = Field(default="127.0.0.1", validation_alias=AliasChoices("DB_HOST", "MYSQL_HOST"))
    DB_PORT: int = Field(default=3306, validation_alias=AliasChoices("DB_PORT", "MYSQL_PORT"))
    DB_USER: str = Field(default="root", validation_alias=AliasChoices("DB_USER", "MYSQL_USER"))
    DB_PASSWORD: str = Field(default="", validation_alias=AliasChoices("DB_PASSWORD", "MYSQL_PASSWORD"))
    DB_NAME: str = Field(default="ai_interview", validation_alias=AliasChoices("DB_NAME", "MYSQL_DATABASE"))

    AI_API_KEY: str = Field(default="", validation_alias=AliasChoices("AI_API_KEY", "DEEPSEEK_API_KEY"))
    AI_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        validation_alias=AliasChoices("AI_BASE_URL", "DEEPSEEK_BASE_URL"),
    )
    AI_MODEL_NAME: str = Field(
        default="deepseek-chat",
        validation_alias=AliasChoices("AI_MODEL_NAME", "DEEPSEEK_MODEL"),
    )
    AI_REQUEST_TIMEOUT: int = Field(
        default=18,
        validation_alias=AliasChoices("AI_REQUEST_TIMEOUT", "DEEPSEEK_REQUEST_TIMEOUT"),
    )
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    @property
    def TORTOISE_ORM(self) -> dict:
        return {
            "connections": {
                "mysql": {
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_NAME,
                    },
                },
            },
            "apps": {
                "models": {
                    "models": ["app.models", "aerich.models"],
                    "default_connection": "mysql",
                },
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai",
        }


settings = Settings()
