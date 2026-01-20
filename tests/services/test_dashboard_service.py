import pytest
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, SQLModel, create_engine

from app.models.payment import Payment, PaymentStatus
from app.models.project import Project
from app.models.unit import Unit, PropertyType
from app.models.user import User, Role
from app.services.dashboard import get_admin_dashboard


def _register_sqlite_date_trunc(engine):
    """
    SQLite does not have date_trunc; provide a minimal compatible impl for tests.
    """
    def date_trunc(part: str, value: str | None):
        if not value:
            return None
        dt = datetime.fromisoformat(value)
        if part == "month":
            return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        return value

    conn = engine.raw_connection()
    conn.create_function("date_trunc", 2, date_trunc)
    conn.commit()
    conn.close()


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    _register_sqlite_date_trunc(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _seed_basics(session: Session):
    client = User(
        fullname="Client",
        email="client@example.com",
        phone="08000000000",
        role=Role.CLIENT,
        hashed_password="hashed",
        is_verified=True,
    )
    project = Project(name="Proj", address="123 Test", num_units=1)
    session.add_all([client, project])
    session.commit()
    session.refresh(client)
    session.refresh(project)

    unit = Unit(
        name="Unit A",
        amount=Decimal("1000000.00"),
        expected_initial_payment=Decimal("200000.00"),
        discount=Decimal("0"),
        comments=None,
        type=PropertyType.DETACHED,
        purchase_date=datetime.now(timezone.utc),
        installment=1,
        payment_plan=False,
        project_id=project.id,
        client_id=client.id,
    )
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return client, project, unit


def test_get_admin_dashboard_returns_expected_counts_and_sums(session: Session):
    _, _, unit = _seed_basics(session)
    now = datetime.now(timezone.utc)

    paid = Payment(
        amount=Decimal("100000.00"),
        due_date=now,
        payment_date=now,
        status=PaymentStatus.PAID,
        unit_id=unit.id,
    )
    unpaid = Payment(
        amount=Decimal("50000.00"),
        due_date=now,
        status=PaymentStatus.NOT_PAID,
        unit_id=unit.id,
    )
    session.add_all([paid, unpaid])
    session.commit()
    session.refresh(paid)
    session.refresh(unpaid)
    print(f"Seeded payments: {paid}, {unpaid}")
    summary = get_admin_dashboard(session)
    print(summary)

    assert summary.total_units == 1
    assert summary.total_payments == 2
    assert summary.total_users == 1
    assert summary.total_projects == 1
    assert summary.total_revenue == pytest.approx(100000.0)
    assert summary.total_outstanding == pytest.approx(50000.0)
    assert len(summary.monthly_revenue) == 12
    assert any(item.amount == pytest.approx(100000.0) for item in summary.monthly_revenue)
    assert len(summary.recent_payments) == 1
    assert summary.recent_payments[0].id == paid.id
