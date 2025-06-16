from pydantic_settings import BaseSettings

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

class Settings(BaseSettings):
    DATABASE_URL: ClassVar[str] = "postgresql+psycopg2://ebubechukwuidam:@localhost:5432/cortts"
    SECRET_KEY:  ClassVar[str] = "corttsRealEstateLimited2013"
    ACCESS_TOKEN_EXPIRE_MINUTES:  ClassVar[int] = 1440

    class Config:
        env_file = ".env"

settings = Settings()