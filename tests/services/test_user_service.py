
import pytest
from sqlmodel import Session, SQLModel, create_engine
from app.services.user_service import *
# Add more specific imports depending on the module functionality

@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_sample_user_service(session):
    assert session is not None
