from typing import Any, Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please configure it in the environment.")

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session() -> Generator[Session, Any, Any]:
    with Session(engine) as session:
        yield session
