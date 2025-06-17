from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from pydantic import (
    AliasChoices,
    AmqpDsn,
    BaseModel,
    Field,
    ImportString,
    PostgresDsn,
    RedisDsn,
)
from typing import ClassVar

from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = Field(default=None, alias="DATABASE_URL")
    SECRET_KEY:  Optional[str] = Field(default=None, alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES:  Optional[int] = Field(default=None, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    R2_ACCESS_KEY_ID:  Optional[str] = Field(default=None, alias="R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY:  Optional[str] = Field(default=None, alias="R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME:  Optional[str] = Field(default=None, alias="R2_BUCKET_NAME")
    R2_ENDPOINT_URL:  Optional[str] = Field(default=None, alias="R2_ENDPOINT_URL")
    R2_ACCESS_TOKEN:  Optional[str] = Field(default=None, alias="R2_ACCESS_TOKEN")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="forbid")

settings = Settings()