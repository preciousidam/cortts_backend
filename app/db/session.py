from sqlmodel import create_engine, Session
from typing import Generator, Any
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL or "", echo=True)

def get_session() -> Generator[Session, Any, Any]:
    with Session(engine) as session:
        yield session