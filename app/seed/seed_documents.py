from sqlmodel import Session, select
from app.db.session import engine
from app.models.document import DocumentTemplate, SignedDocument
from app.models.unit import Unit
from app.models.user import User, Role
from datetime import datetime, timezone


def seed_documents():
    with Session(engine) as session:
        unit = session.exec(select(Unit)).first()
        client = session.exec(select(User).where(User.role == Role.CLIENT)).first()
        agent = session.exec(select(User).where(User.role == Role.AGENT)).first()

        if unit:
            template = DocumentTemplate(
                name="Sale Agreement Template",
                link="https://example.com/template.pdf",
                unit_id=unit.id
            )
            session.add(template)

            signed_by_client = SignedDocument(
                name="Signed Sale Agreement - Client",
                link="https://example.com/signed-client.pdf",
                unit_id=unit.id,
                client_id=client.id if client else None
            )
            signed_by_agent = SignedDocument(
                name="Signed Sale Agreement - Agent",
                link="https://example.com/signed-agent.pdf",
                unit_id=unit.id,
                agent_id=agent.id if agent else None
            )
            session.add_all([signed_by_client, signed_by_agent])
            session.commit()


if __name__ == "__main__":
    seed_documents()