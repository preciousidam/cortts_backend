import pytest
from uuid import uuid4
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from app.core.security import verify_password
from app.models.company import Company  # noqa: F401  # ensure FK tables exist
from app.models.user import Role, User
from app.schemas.paging import Paging
from app.schemas.user import RegisterRequest, UserUpdate
from app.services import user_service
from app.services.user_service import (
    authenticate_user,
    create_user,
    forgot_password,
    get_all_users,
    get_user_by_id,
    logout_user,
    reset_password,
    soft_delete_user,
    update_user,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def deterministic_code(monkeypatch):
    monkeypatch.setattr(user_service.random, "randint", lambda _a, _b: 123456)


def test_create_user_persists_and_hashes_password(session: Session):
    request = RegisterRequest(
        email="TEST@Example.com",
        password="Secret123",
        fullname="Test User",
        phone="08000000000",
    )

    user = create_user(session, request)

    assert user.email == "test@example.com"
    assert user.fullname == "Test User"
    assert user.verification_code == "123456"
    assert verify_password("Secret123", user.hashed_password)
    assert user.is_verified is False


def test_create_user_requires_mandatory_fields(session: Session):
    request = RegisterRequest(
        email="test@example.com",
        password="Secret123",
        fullname="Test User",
        phone=None,
    )

    with pytest.raises(HTTPException) as exc:
        create_user(session, request)

    assert exc.value.status_code == 400


def test_create_user_prevents_duplicate_email_or_phone(session: Session):
    create_user(
        session,
        RegisterRequest(
            email="dupe@example.com",
            password="Secret123",
            fullname="Existing",
            phone="08000000000",
        ),
    )

    with pytest.raises(HTTPException) as exc:
        create_user(
            session,
            RegisterRequest(
                email="dupe@example.com",
                password="Secret123",
                fullname="Duplicate",
                phone="08000000000",
            ),
        )

    assert exc.value.status_code == 409


def test_authenticate_user_returns_none_on_wrong_password(session: Session):
    create_user(
        session,
        RegisterRequest(
            email="auth@example.com",
            password="CorrectPass",
            fullname="Auth User",
            phone="08000000001",
        ),
    )

    assert authenticate_user(session, "auth@example.com", "WrongPass") is None


def test_authenticate_user_requires_verification(session: Session):
    user = create_user(
        session,
        RegisterRequest(
            email="verify@example.com",
            password="Secret123",
            fullname="Verify User",
            phone="08000000002",
        ),
    )

    with pytest.raises(HTTPException) as exc:
        authenticate_user(session, "verify@example.com", "Secret123")

    assert exc.value.status_code == 403
    user.is_verified = True
    session.add(user)
    session.commit()
    authenticated = authenticate_user(session, "verify@example.com", "Secret123")
    assert authenticated.id == user.id


def test_get_all_users_supports_filters_and_search(session: Session):
    admin = create_user(
        session,
        RegisterRequest(
            email="admin@example.com",
            password="Secret123",
            fullname="Admin User",
            phone="08000000003",
        ),
    )
    admin.role = Role.ADMIN
    client = create_user(
        session,
        RegisterRequest(
            email="client@example.com",
            password="Secret123",
            fullname="Client Person",
            phone="08000000004",
        ),
    )
    session.add_all([admin, client])
    session.commit()

    filtered = get_all_users(session, Paging(), filter={"role": Role.ADMIN})
    searched = get_all_users(session, Paging(), q="Client")

    assert filtered["total"] == 1
    assert filtered["data"][0].id == admin.id
    assert searched["total"] == 1
    assert searched["data"][0].id == client.id


def test_get_user_by_id_returns_record(session: Session):
    user = create_user(
        session,
        RegisterRequest(
            email="fetch@example.com",
            password="Secret123",
            fullname="Fetcher",
            phone="08000000005",
        ),
    )

    found = get_user_by_id(session, user.id)

    assert found is not None
    assert found.email == "fetch@example.com"


def test_update_user_persists_changes(session: Session):
    user = create_user(
        session,
        RegisterRequest(
            email="update@example.com",
            password="Secret123",
            fullname="Updatable",
            phone="08000000006",
        ),
    )

    updated = update_user(
        session,
        user.id,
        UserUpdate(fullname="Updated Name", phone="08099999999", role=Role.ADMIN),
    )

    assert updated.fullname == "Updated Name"
    assert updated.phone == "08099999999"
    assert updated.role == Role.ADMIN


def test_soft_delete_user_sets_flags(session: Session):
    user = create_user(
        session,
        RegisterRequest(
            email="delete@example.com",
            password="Secret123",
            fullname="Delete Me",
            phone="08000000007",
        ),
    )

    deleted = soft_delete_user(session, user.id, reason="requested")

    assert deleted.deleted is True
    assert deleted.reason_for_delete == "requested"
    assert deleted.deleted_at is not None


def test_forgot_password_updates_verification_code(session: Session):
    user = create_user(
        session,
        RegisterRequest(
            email="resetme@example.com",
            password="Secret123",
            fullname="Reset Me",
            phone="08000000008",
        ),
    )
    user.verification_code = "000000"
    session.add(user)
    session.commit()

    updated = forgot_password(session, user.email)

    assert updated.verification_code == "123456"
    assert updated.id == user.id


def test_reset_password_validates_code(session: Session):
    user = create_user(
        session,
        RegisterRequest(
            email="code@example.com",
            password="OldPass",
            fullname="Code User",
            phone="08000000009",
        ),
    )
    user.verification_code = "999999"
    user.is_verified = True
    session.add(user)
    session.commit()

    with pytest.raises(HTTPException) as exc:
        reset_password(session, user.email, "wrong", "NewPass")
    assert exc.value.status_code == 400

    updated = reset_password(session, user.email, "999999", "NewPass")

    assert verify_password("NewPass", updated.hashed_password)
    assert updated.verification_code is None


def test_logout_user_raises_for_missing_user(session: Session):
    with pytest.raises(HTTPException) as exc:
        logout_user(session, user_id=uuid4())

    assert exc.value.status_code == 404

    user = create_user(
        session,
        RegisterRequest(
            email="logout@example.com",
            password="Secret123",
            fullname="Logout User",
            phone="08000000010",
        ),
    )
    assert logout_user(session, user.id) is None
