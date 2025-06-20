from sqlmodel import Session
from app.db.session import engine
from app.models.unit import Unit
from app.models.unit_agent_link import UnitAgentLink, AgentRole
from app.models.payment import Payment, PaymentStatus
from app.models.project import Project
from app.models.user import User, Role
from datetime import datetime, timezone


def seed():
    with Session(engine) as session:
        # Agents (now as Users)
        internal_agent = User(
            fullname="Jane Doe",
            email="jane@cortts.com",
            phone="08012345678",
            hashed_password="notused",
            address="Lagos HQ",
            role=Role.AGENT,
            is_internal=True,
            commission_rate=0.05,
            is_verified=True
        )
        external_agent = User(
            fullname="John Contractor",
            email="john@contractor.com",
            phone="08087654321",
            hashed_password="notused",
            address="Abuja",
            role=Role.AGENT,
            is_internal=False,
            commission_rate=0.03,
            is_verified=True
        )
        session.add_all([internal_agent, external_agent])
        session.commit()

        # Project
        project = Project(
            name="Coral Estate",
            description="Luxury homes in Lekki",
            address="Lekki Phase 1, Lagos",
            num_units=10,
            purpose="Residential"
        )
        session.add(project)
        session.commit()

        # Client (now as User)
        client = User(
            fullname="Chinedu Obi",
            email="chinedu@client.com",
            phone="08099998888",
            hashed_password="notused",
            address="Ajah, Lagos",
            role=Role.CLIENT,
            is_verified=True
        )
        session.add(client)
        session.commit()

        # Unit
        unit = Unit(
            name="Terrace B4",
            amount=45000000.00,
            expected_initial_payment=5000000.00,
            discount=0.0,
            comments="Test unit",
            type="Terrace",
            purchase_date=datetime.now(timezone.utc),
            installment=6,
            payment_plan=True,
            project_id=project.id,
            client_id=client.id
        )

        unit2 = Unit(
            name="Semi-Detached A1",
            amount=60000000.00,
            expected_initial_payment=7000000.00,
            discount=0.0,
            comments="Another test unit",
            type="Semi-Detached",
            purchase_date=datetime.now(timezone.utc),
            installment=12,
            payment_plan=True,
            project_id=project.id,
            client_id=client.id
        )
        session.add_all([unit, unit2])
        session.commit()

        payment = Payment(
            amount=5000000.0,
            due_date=datetime.now(timezone.utc),
            status=PaymentStatus.PAID,
            unit_id=unit.id,
        )
        session.add(payment)
        session.commit()

        # Unit-Agent Links
        session.add_all([
            UnitAgentLink(unit_id=unit.id, agent_id=internal_agent.id, role=AgentRole.sales_rep),
            UnitAgentLink(unit_id=unit.id, agent_id=external_agent.id, role=AgentRole.external_agent),
        ])
        session.commit()


if __name__ == "__main__":
    seed()