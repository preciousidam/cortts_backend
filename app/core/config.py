from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = Field(default=None, alias="DATABASE_URL")
    SECRET_KEY:  Optional[str] = Field(default=None, alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES:  Optional[int] = Field(default=None, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    R2_ACCESS_KEY_ID:  Optional[str] = Field(default=None, alias="R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY:  Optional[str] = Field(default=None, alias="R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME:  Optional[str] = Field(default=None, alias="R2_BUCKET_NAME")
    R2_ENDPOINT_URL:  Optional[str] = Field(default=None, alias="R2_ENDPOINT_URL")
    R2_ACCESS_TOKEN:  Optional[str] = Field(default=None, alias="R2_ACCESS_TOKEN")
    R2_PUBLIC_URL:  Optional[str] = Field(default=None, alias="R2_PUBLIC_URL")
    OPENAI_API_KEY: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"], alias="ALLOWED_ORIGINS"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="forbid")

settings = Settings()
