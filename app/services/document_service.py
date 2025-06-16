from sqlmodel import Session, select
from app.models.document import DocumentTemplate, SignedDocument


# Document Template
def create_template(session: Session, data):
    record = DocumentTemplate(**data.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_unit_templates(session: Session, unit_id: str):
    return session.exec(select(DocumentTemplate).where(DocumentTemplate.unit_id == unit_id)).all()


# Signed Document
def create_signed_doc(session: Session, data):
    record = SignedDocument(**data.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_signed_docs_for_unit(session: Session, unit_id: str):
    return session.exec(select(SignedDocument).where(SignedDocument.unit_id == unit_id)).all()


def get_signed_docs_for_client(session: Session, client_id: str):
    return session.exec(select(SignedDocument).where(SignedDocument.client_id == client_id)).all()


def get_signed_docs_for_agent(session: Session, agent_id: str):
    return session.exec(select(SignedDocument).where(SignedDocument.agent_id == agent_id)).all()