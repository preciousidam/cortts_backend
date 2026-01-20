import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from app.models.user import User, Role
from app.models.project import Project
from app.models.unit import Unit, PropertyType
from app.models.payment import Payment, PaymentStatus
from app.services.unit_service import create_unit, update_unit
from datetime import datetime, timezone
from app.schemas.unit import UnitCreate, UnitUpdate

@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def seed_client_and_project(session):
    client = User(
        fullname="Test Client",
        email="client@example.com",
        phone="08000000000",
        role=Role.CLIENT,
        hashed_password="hashed",
        is_verified=True
    )
    project = Project(
        name="Test Project",
        address="123 Test Street",
        num_units=5
    )
    session.add_all([client, project])
    session.commit()
    return client, project

def test_create_unit_and_payments(session, seed_client_and_project):
    client, project = seed_client_and_project
    data = UnitCreate(
        name="Test Unit A",
        amount=10000000,
        expected_initial_payment=2000000,
        discount=0,
        comments=None,
        type=PropertyType.TERRACED,
        purchase_date=datetime.now(timezone.utc),
        installment=4,
        payment_plan=True,
        project_id=project.id,
        client_id=client.id
    )
    unit = create_unit(session, data)
    payments = session.exec(select(Payment).where(Payment.unit_id == unit.id)).all()
    assert len(payments) == 5  # 1 initial + 4 installments
    assert any(p.status == PaymentStatus.PAID for p in payments) == False

def test_update_unit_recalculates_payments(session, seed_client_and_project):
    client, project = seed_client_and_project
    data = UnitCreate(
        name="Test Unit B",
        amount=12000000,
        expected_initial_payment=3000000,
        discount=0,
        comments=None,
        type=PropertyType.DUPLEX,
        purchase_date=datetime.now(timezone.utc),
        installment=3,
        payment_plan=True,
        project_id=project.id,
        client_id=client.id
    )
    unit = create_unit(session, data)
    update_data = UnitUpdate(
        expected_initial_payment=4000000,
        installment=2
    )
    updated = update_unit(session, unit.id, update_data)
    unpaid_payments = [p for p in updated.payments if p.status == PaymentStatus.NOT_PAID and not p.deleted]
    assert len(unpaid_payments) == 3