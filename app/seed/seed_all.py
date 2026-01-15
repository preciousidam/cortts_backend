from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.session import engine
from app.models.company import Company
from app.models.document import DocumentTemplate, MediaFile, SignedDocument
from app.models.notification import Notification
from app.models.payment import Payment, PaymentStatus
from app.models.project import Project, ProjectPurpose
from app.models.push_token import PushToken
from app.models.unit import PaymentDuration, PropertyType, Unit, UnitCompletionStatus
from app.models.unit_agent_link import AgentRole, UnitAgentLink
from app.models.user import Role, User


def _get_or_create_company(session: Session, data: dict) -> Company:
    existing = session.exec(select(Company).where(Company.name == data["name"])).first()
    if existing:
        return existing
    company = Company(**data)
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


def _get_or_create_user(session: Session, data: dict) -> User:
    existing = session.exec(select(User).where(User.email == data["email"])).first()
    if existing:
        return existing
    password = data.pop("password")
    user = User(**data, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _get_or_create_project(session: Session, data: dict) -> Project:
    existing = session.exec(select(Project).where(Project.name == data["name"])).first()
    if existing:
        return existing
    project = Project(**data)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def _get_or_create_unit(session: Session, data: dict) -> Unit:
    existing = session.exec(
        select(Unit).where(Unit.name == data["name"], Unit.project_id == data["project_id"])
    ).first()
    if existing:
        return existing
    unit = Unit(**data)
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit


def _get_or_create_link(
    session: Session, unit_id, agent_id, role: AgentRole = AgentRole.sales_rep
) -> UnitAgentLink:
    existing = session.exec(
        select(UnitAgentLink).where(
            UnitAgentLink.unit_id == unit_id,
            UnitAgentLink.agent_id == agent_id,
            UnitAgentLink.role == role,
        )
    ).first()
    if existing:
        return existing
    link = UnitAgentLink(unit_id=unit_id, agent_id=agent_id, role=role)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def _get_or_create_media(session: Session, data: dict) -> MediaFile:
    existing = session.exec(select(MediaFile).where(MediaFile.file_path == data["file_path"])).first()
    if existing:
        return existing
    media = MediaFile(**data)
    session.add(media)
    session.commit()
    session.refresh(media)
    return media


def _get_or_create_document_template(session: Session, data: dict) -> DocumentTemplate:
    existing = session.exec(
        select(DocumentTemplate).where(
            DocumentTemplate.unit_id == data["unit_id"], DocumentTemplate.name == data["name"]
        )
    ).first()
    if existing:
        return existing
    template = DocumentTemplate(**data)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


def _get_or_create_signed_document(session: Session, data: dict) -> SignedDocument:
    existing = session.exec(
        select(SignedDocument).where(
            SignedDocument.unit_id == data["unit_id"],
            SignedDocument.name == data["name"],
            SignedDocument.client_id == data.get("client_id"),
            SignedDocument.agent_id == data.get("agent_id"),
        )
    ).first()
    if existing:
        return existing
    signed = SignedDocument(**data)
    session.add(signed)
    session.commit()
    session.refresh(signed)
    return signed


def _get_or_create_payment(session: Session, data: dict) -> Payment:
    existing = session.exec(
        select(Payment).where(
            Payment.unit_id == data["unit_id"],
            Payment.amount == data["amount"],
            Payment.due_date == data.get("due_date"),
            Payment.reason_for_payment == data.get("reason_for_payment"),
        )
    ).first()
    if existing:
        return existing
    payment = Payment(**data)
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


def _get_or_create_notification(session: Session, data: dict) -> Notification:
    existing = session.exec(
        select(Notification).where(
            Notification.user_id == data["user_id"], Notification.title == data["title"]
        )
    ).first()
    if existing:
        return existing
    notification = Notification(**data)
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


def _get_or_create_push_token(session: Session, data: dict) -> PushToken:
    existing = session.exec(select(PushToken).where(PushToken.token == data["token"])).first()
    if existing:
        return existing
    push_token = PushToken(**data)
    session.add(push_token)
    session.commit()
    session.refresh(push_token)
    return push_token


def seed_all() -> None:
    with Session(engine) as session:
        companies = {
            "cortts": _get_or_create_company(
                session,
                {
                    "name": "Cortts Realty",
                    "address": "Lagos HQ, Nigeria",
                    "phone": "08010001000",
                    "email": "contact@cortts.com",
                },
            ),
            "northbridge": _get_or_create_company(
                session,
                {
                    "name": "Northbridge Estates",
                    "address": "Abuja Office, Nigeria",
                    "phone": "08120002000",
                    "email": "partners@northbridge.com",
                },
            ),
        }

        users = {
            "admin": _get_or_create_user(
                session,
                {
                    "fullname": "Precious Idam",
                    "email": "precious@example.com",
                    "phone": "08162300796",
                    "password": "precious42idam",
                    "address": "HQ",
                    "role": Role.ADMIN,
                    "is_verified": True,
                    "is_active": True,
                },
            ),
            "internal_agent": _get_or_create_user(
                session,
                {
                    "fullname": "Ada Sales",
                    "email": "ada@cortts.com",
                    "phone": "08020002000",
                    "password": "agentPass123!",
                    "address": "Lekki, Lagos",
                    "role": Role.AGENT,
                    "is_verified": True,
                    "commission_rate": 0.05,
                    "is_internal": True,
                    "company_id": companies["cortts"].id,
                },
            ),
            "external_agent": _get_or_create_user(
                session,
                {
                    "fullname": "Bola Contractor",
                    "email": "bola@northbridge.com",
                    "phone": "08030003000",
                    "password": "externalAgent!",
                    "address": "Wuse, Abuja",
                    "role": Role.AGENT,
                    "is_verified": True,
                    "commission_rate": 0.03,
                    "is_internal": False,
                    "company_id": companies["northbridge"].id,
                },
            ),
            "client_one": _get_or_create_user(
                session,
                {
                    "fullname": "Kemi Client",
                    "email": "kemi.client@example.com",
                    "phone": "08040004000",
                    "password": "clientDemo1!",
                    "address": "Victoria Island, Lagos",
                    "role": Role.CLIENT,
                    "is_verified": True,
                },
            ),
            "client_two": _get_or_create_user(
                session,
                {
                    "fullname": "Tony Client",
                    "email": "tony.client@example.com",
                    "phone": "08050005000",
                    "password": "clientDemo2!",
                    "address": "Garki, Abuja",
                    "role": Role.CLIENT,
                    "is_verified": True,
                },
            ),
        }

        now = datetime.now(timezone.utc)
        projects = {
            "coral": _get_or_create_project(
                session,
                {
                    "name": "Coral Estate",
                    "description": "Luxury homes in Lekki with waterfront access",
                    "address": "Lekki Phase 1, Lagos",
                    "num_units": 20,
                    "purpose": ProjectPurpose.RESIDENTIAL,
                    "artwork_url": "/media/projects/coral-estate-front.jpg",
                },
            ),
            "palm": _get_or_create_project(
                session,
                {
                    "name": "Palm Heights",
                    "description": "Mixed-use highrise with serviced apartments",
                    "address": "Central Business District, Abuja",
                    "num_units": 32,
                    "purpose": ProjectPurpose.MIXED_USE,
                    "artwork_url": "/media/projects/palm-heights.jpg",
                },
            ),
        }

        units = {
            "coral_terrace_b4": _get_or_create_unit(
                session,
                {
                    "name": "Terrace B4",
                    "amount": 45_000_000.00,
                    "expected_initial_payment": 5_000_000.00,
                    "discount": 0.0,
                    "comments": "Payment plan for Kemi's family home.",
                    "type": PropertyType.TERRACED,
                    "purchase_date": now - timedelta(days=14),
                    "installment": 6,
                    "payment_plan": True,
                    "project_id": projects["coral"].id,
                    "client_id": users["client_one"].id,
                    "handover_date": now + timedelta(days=180),
                    "payment_duration": PaymentDuration.MONTHLY,
                    "development_status": UnitCompletionStatus.IN_PROGRESS,
                },
            ),
            "coral_semi_a1": _get_or_create_unit(
                session,
                {
                    "name": "Semi-Detached A1",
                    "amount": 60_000_000.00,
                    "expected_initial_payment": 7_000_000.00,
                    "discount": 2.5,
                    "comments": "Investor package with extended plan.",
                    "type": PropertyType.SEMI_DETACHED,
                    "purchase_date": now - timedelta(days=30),
                    "installment": 12,
                    "payment_plan": True,
                    "project_id": projects["coral"].id,
                    "client_id": users["client_two"].id,
                    "handover_date": now + timedelta(days=240),
                    "payment_duration": PaymentDuration.MONTHLY,
                    "development_status": UnitCompletionStatus.IN_PROGRESS,
                },
            ),
            "palm_penthouse": _get_or_create_unit(
                session,
                {
                    "name": "Penthouse 12",
                    "amount": 85_000_000.00,
                    "expected_initial_payment": 10_000_000.00,
                    "discount": 0.0,
                    "comments": "Top-floor unit with panoramic views.",
                    "type": PropertyType.PENTHOUSE,
                    "purchase_date": now - timedelta(days=10),
                    "installment": 10,
                    "payment_plan": True,
                    "project_id": projects["palm"].id,
                    "client_id": users["client_one"].id,
                    "handover_date": now + timedelta(days=300),
                    "payment_duration": PaymentDuration.MONTHLY,
                    "development_status": UnitCompletionStatus.NOT_STARTED,
                },
            ),
            "palm_studio": _get_or_create_unit(
                session,
                {
                    "name": "Studio 04",
                    "amount": 25_000_000.00,
                    "expected_initial_payment": 3_000_000.00,
                    "discount": 0.0,
                    "comments": "Available furnished studio.",
                    "type": PropertyType.STUDIO,
                    "purchase_date": None,
                    "installment": 6,
                    "payment_plan": False,
                    "project_id": projects["palm"].id,
                    "client_id": None,
                    "handover_date": None,
                    "payment_duration": PaymentDuration.MONTHLY,
                    "development_status": UnitCompletionStatus.NOT_STARTED,
                },
            ),
        }

        _get_or_create_link(session, units["coral_terrace_b4"].id, users["internal_agent"].id, AgentRole.sales_rep)
        _get_or_create_link(session, units["coral_terrace_b4"].id, users["external_agent"].id, AgentRole.external_agent)
        _get_or_create_link(session, units["coral_semi_a1"].id, users["internal_agent"].id, AgentRole.sales_rep)
        _get_or_create_link(session, units["palm_penthouse"].id, users["external_agent"].id, AgentRole.external_agent)

        _get_or_create_media(
            session,
            {
                "file_name": "Coral Estate Artwork.jpg",
                "file_type": "image/jpeg",
                "file_path": "/media/projects/coral-estate-front.jpg",
                "file_size": 480_000,
                "project_id": projects["coral"].id,
                "uploaded_by": users["internal_agent"].id,
            },
        )
        _get_or_create_media(
            session,
            {
                "file_name": "Palm Heights Artwork.jpg",
                "file_type": "image/jpeg",
                "file_path": "/media/projects/palm-heights.jpg",
                "file_size": 525_000,
                "project_id": projects["palm"].id,
                "uploaded_by": users["external_agent"].id,
            },
        )

        terrace_image = _get_or_create_media(
            session,
            {
                "file_name": "Terrace B4 Front.jpg",
                "file_type": "image/jpeg",
                "file_path": "/media/units/coral-terrace-b4.jpg",
                "file_size": 512_000,
                "unit_id": units["coral_terrace_b4"].id,
                "uploaded_by": users["internal_agent"].id,
            },
        )
        semi_image = _get_or_create_media(
            session,
            {
                "file_name": "Semi Detached A1.jpg",
                "file_type": "image/jpeg",
                "file_path": "/media/units/coral-semi-a1.jpg",
                "file_size": 496_000,
                "unit_id": units["coral_semi_a1"].id,
                "uploaded_by": users["external_agent"].id,
            },
        )
        penthouse_image = _get_or_create_media(
            session,
            {
                "file_name": "Penthouse 12 Living Room.jpg",
                "file_type": "image/jpeg",
                "file_path": "/media/units/palm-penthouse-12.jpg",
                "file_size": 604_000,
                "unit_id": units["palm_penthouse"].id,
                "uploaded_by": users["internal_agent"].id,
            },
        )
        _get_or_create_media(
            session,
            {
                "file_name": "Palm Studio 04.jpg",
                "file_type": "image/jpeg",
                "file_path": "/media/units/palm-studio-04.jpg",
                "file_size": 388_000,
                "unit_id": units["palm_studio"].id,
                "uploaded_by": users["external_agent"].id,
            },
        )

        template_media = _get_or_create_media(
            session,
            {
                "file_name": "Sale Agreement - Coral Terrace.pdf",
                "file_type": "application/pdf",
                "file_path": "/media/documents/coral-terrace-agreement.pdf",
                "file_size": 220_000,
                "unit_id": units["coral_terrace_b4"].id,
                "uploaded_by": users["internal_agent"].id,
            },
        )
        coral_template = _get_or_create_document_template(
            session,
            {
                "name": "Sale Agreement Template - Terrace B4",
                "media_file_id": template_media.id,
                "unit_id": units["coral_terrace_b4"].id,
            },
        )
        _get_or_create_signed_document(
            session,
            {
                "name": "Signed Agreement - Client",
                "media_file_id": template_media.id,
                "unit_id": units["coral_terrace_b4"].id,
                "client_id": users["client_one"].id,
            },
        )
        _get_or_create_signed_document(
            session,
            {
                "name": "Signed Agreement - Agent",
                "media_file_id": template_media.id,
                "unit_id": units["coral_terrace_b4"].id,
                "agent_id": users["internal_agent"].id,
            },
        )

        penthouse_template_media = _get_or_create_media(
            session,
            {
                "file_name": "Palm Heights Contract.pdf",
                "file_type": "application/pdf",
                "file_path": "/media/documents/palm-heights-contract.pdf",
                "file_size": 310_000,
                "unit_id": units["palm_penthouse"].id,
                "uploaded_by": users["external_agent"].id,
            },
        )
        _get_or_create_document_template(
            session,
            {
                "name": "Palm Heights Purchase Contract",
                "media_file_id": penthouse_template_media.id,
                "unit_id": units["palm_penthouse"].id,
            },
        )
        _get_or_create_signed_document(
            session,
            {
                "name": "Signed Contract - Client",
                "media_file_id": penthouse_template_media.id,
                "unit_id": units["palm_penthouse"].id,
                "client_id": users["client_one"].id,
            },
        )

        _get_or_create_payment(
            session,
            {
                "reason_for_payment": "Initial Deposit",
                "amount": 5_000_000.0,
                "due_date": now - timedelta(days=12),
                "payment_date": now - timedelta(days=12),
                "status": PaymentStatus.PAID,
                "unit_id": units["coral_terrace_b4"].id,
            },
        )
        _get_or_create_payment(
            session,
            {
                "reason_for_payment": "Second Installment",
                "amount": 6_666_666.67,
                "due_date": now + timedelta(days=20),
                "payment_date": None,
                "status": PaymentStatus.NOT_PAID,
                "unit_id": units["coral_terrace_b4"].id,
            },
        )
        _get_or_create_payment(
            session,
            {
                "reason_for_payment": "Third Installment",
                "amount": 6_666_666.67,
                "due_date": now - timedelta(days=5),
                "payment_date": None,
                "status": PaymentStatus.OVERDUE,
                "unit_id": units["coral_terrace_b4"].id,
            },
        )
        _get_or_create_payment(
            session,
            {
                "reason_for_payment": "Deposit",
                "amount": 7_000_000.0,
                "due_date": now - timedelta(days=25),
                "payment_date": now - timedelta(days=25),
                "status": PaymentStatus.PAID,
                "unit_id": units["coral_semi_a1"].id,
            },
        )
        _get_or_create_payment(
            session,
            {
                "reason_for_payment": "Contract Signing",
                "amount": 3_000_000.0,
                "due_date": now + timedelta(days=15),
                "payment_date": None,
                "status": PaymentStatus.NOT_PAID,
                "unit_id": units["palm_penthouse"].id,
            },
        )

        _get_or_create_notification(
            session,
            {
                "user_id": users["client_one"].id,
                "title": "Welcome to Coral Estate",
                "body": "Your unit Terrace B4 has been reserved and first payment received.",
                "data": {"unit_id": str(units["coral_terrace_b4"].id)},
            },
        )
        _get_or_create_notification(
            session,
            {
                "user_id": users["internal_agent"].id,
                "title": "New Assignment",
                "body": "You have been assigned as sales rep for Terrace B4.",
                "data": {
                    "unit_id": str(units["coral_terrace_b4"].id),
                    "project_id": str(projects["coral"].id),
                },
            },
        )
        _get_or_create_notification(
            session,
            {
                "user_id": users["external_agent"].id,
                "title": "Document Signed",
                "body": "Palm Heights contract has been signed by the client.",
                "data": {"unit_id": str(units["palm_penthouse"].id)},
            },
        )

        _get_or_create_push_token(
            session,
            {
                "user_id": users["internal_agent"].id,
                "token": "ExponentPushToken[demo-agent-token]",
                "device": "iPhone 15 Pro",
            },
        )
        _get_or_create_push_token(
            session,
            {
                "user_id": users["client_one"].id,
                "token": "ExponentPushToken[demo-client-token]",
                "device": "Pixel 7",
            },
        )

        print("Seeded companies, users, projects, units, payments, documents, notifications, and push tokens.")


if __name__ == "__main__":
    seed_all()
