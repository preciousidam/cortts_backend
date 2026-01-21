
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.document import MediaFile
from app.models.payment import Payment
from app.models.project import Project
from app.models.unit import Unit
from app.models.user import Role, User
from app.schemas.paging import Paging
from app.schemas.payment import PaymentCreate, PaymentStatus, PaymentUpdate
from app.services.payment_service import (
    create_payment,
    get_all_payments,
    get_payment_by_id,
    get_payments_by_unit,
    soft_delete_payment,
    update_payment,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def unit(session: Session) -> Unit:
    client = User(
        fullname="Client",
        email="client@example.com",
        phone="08012345678",
        role=Role.CLIENT,
        hashed_password="hashed",
        is_verified=True,
    )
    project = Project(name="Project One", address="123 Street", num_units=1)
    session.add_all([client, project])
    session.commit()
    unit = Unit(
        name="Unit A",
        amount=1_000_000,
        expected_initial_payment=200_000,
        discount=0,
        type=None,
        purchase_date=datetime.now(timezone.utc),
        installment=2,
        payment_plan=True,
        project_id=project.id,
        client_id=client.id,
    )
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit


@pytest.fixture
def media_file(session: Session, unit: Unit) -> MediaFile:
    media = MediaFile(
        file_type="image/png",
        file_name="receipt.png",
        file_path="https://example.com/receipt.png",
        file_size=123,
        unit_id=unit.id,
    )
    session.add(media)
    session.commit()
    session.refresh(media)
    return media


def test_create_payment_persists_with_uuid_conversion(session: Session, unit: Unit):
    payment_data = PaymentCreate(
        reason_for_payment="First",
        amount=500_000,
        unit_id=unit.id,
    )

    payment = create_payment(session, payment_data)
    fetched = session.get(Payment, payment.id)

    assert fetched is not None
    assert fetched.unit_id == unit.id
    assert fetched.amount == 500_000
    assert fetched.status == PaymentStatus.NOT_PAID


def test_create_paid_payment_requires_receipt(session: Session, unit: Unit):
    payment_data = PaymentCreate(
        reason_for_payment="Paid without receipt",
        amount=500_000,
        unit_id=unit.id,
        status=PaymentStatus.PAID,
    )

    with pytest.raises(HTTPException) as exc:
        create_payment(session, payment_data)

    assert exc.value.status_code == 400
    assert "Media ID" in exc.value.detail


def test_create_paid_payment_with_receipt_sets_payment_date(session: Session, unit: Unit, media_file: MediaFile):
    payment_data = PaymentCreate(
        reason_for_payment="Paid with receipt",
        amount=500_000,
        unit_id=unit.id,
        status=PaymentStatus.PAID,
        media_id=media_file.id,
    )

    payment = create_payment(session, payment_data)

    assert payment.media_id == media_file.id
    assert payment.payment_date is not None


def test_get_all_payments_excludes_deleted(session: Session, unit: Unit):
    active = create_payment(
        session,
        PaymentCreate(reason_for_payment="Active", amount=100, unit_id=unit.id),
    )
    deleted = create_payment(
        session,
        PaymentCreate(reason_for_payment="Deleted", amount=50, unit_id=unit.id),
    )
    deleted.deleted = True
    session.add(deleted)
    session.commit()

    result = get_all_payments(session, Paging())

    assert result["total"] == 1
    assert result["data"][0].id == active.id


def test_get_payments_by_unit_filters_unit_only(session: Session, unit: Unit):
    other_unit = Unit(
        name="Unit B",
        amount=900_000,
        expected_initial_payment=100_000,
        discount=0,
        type=None,
        purchase_date=datetime.now(timezone.utc),
        installment=1,
        payment_plan=False,
        project_id=unit.project_id,
        client_id=unit.client_id,
    )
    session.add(other_unit)
    session.commit()
    session.refresh(other_unit)

    first = create_payment(
        session,
        PaymentCreate(reason_for_payment="U1", amount=100, unit_id=unit.id),
    )
    create_payment(
        session,
        PaymentCreate(reason_for_payment="U2", amount=200, unit_id=other_unit.id),
    )

    result = get_payments_by_unit(session, unit.id, Paging())

    assert result["total"] == 1
    assert result["data"][0].id == first.id


def test_get_payment_by_id_returns_match(session: Session, unit: Unit):
    payment = create_payment(
        session,
        PaymentCreate(reason_for_payment="Lookup", amount=150, unit_id=unit.id),
    )

    found = get_payment_by_id(session, payment.id)

    assert found is not None
    assert found.reason_for_payment == "Lookup"


def test_update_payment_paid_requires_receipt(session: Session, unit: Unit):
    payment = create_payment(
        session,
        PaymentCreate(reason_for_payment="Receipt Needed", amount=300, unit_id=unit.id),
    )

    with pytest.raises(HTTPException) as exc:
        update_payment(session, payment.id, PaymentUpdate(status=PaymentStatus.PAID))

    assert exc.value.status_code == 400
    assert "Media ID" in exc.value.detail


def test_update_payment_to_paid_sets_payment_date_when_media_present(
    session: Session, unit: Unit, media_file: MediaFile
):
    payment = create_payment(
        session,
        PaymentCreate(reason_for_payment="To Paid", amount=400, unit_id=unit.id),
    )
    updated = update_payment(
        session,
        payment.id,
        PaymentUpdate(status=PaymentStatus.PAID, media_id=media_file.id),
    )

    assert updated.payment_date is not None
    assert updated.media_id == media_file.id


def test_update_payment_to_not_paid_clears_payment_date_and_media(session: Session, unit: Unit):
    payment = create_payment(
        session,
        PaymentCreate(reason_for_payment="Reset", amount=500, unit_id=unit.id),
    )
    payment.media_id = uuid4()
    payment.payment_date = datetime.now(timezone.utc)
    session.add(payment)
    session.commit()

    updated = update_payment(
        session,
        payment.id,
        PaymentUpdate(status=PaymentStatus.NOT_PAID),
    )

    assert updated.payment_date is None
    assert updated.media_id is None


def test_soft_delete_payment_marks_deleted(session: Session, unit: Unit):
    payment = create_payment(
        session,
        PaymentCreate(reason_for_payment="Delete", amount=600, unit_id=unit.id),
    )

    deleted = soft_delete_payment(session, payment.id, reason="duplicate")
    refreshed = session.exec(select(Payment).where(Payment.id == payment.id)).one()

    assert deleted.deleted is True
    assert deleted.reason_for_delete == "duplicate"
    assert refreshed.deleted is True
