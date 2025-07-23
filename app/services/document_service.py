from sqlmodel import Session, select
from typing import Sequence
from datetime import datetime, timezone
from app.models.document import DocumentTemplate, SignedDocument
from .notification_service import create_notification
from app.schemas.document import DocumentTemplateCreate, DocumentTemplateRead, SignedDocumentCreate, SignedDocumentRead, DocumentTemplateUpdate, SignedDocumentUpdate


# Document Template
def create_template(session: Session, data: DocumentTemplateCreate) -> DocumentTemplate | None:
    """
    Creates a new document template in the database.
    :param session: SQLAlchemy session object
    :param data: Data model containing the document template details
    :return: The created DocumentTemplate object
    """
    data_dict = data.model_dump()

    if ("media_file_id" not in data_dict or
            data_dict["media_file_id"] is None):
        return None
        
    record = DocumentTemplate(**data_dict)
    session.add(record)
    session.commit()
    session.refresh(record)

    return record

def get_templates(session: Session) -> Sequence[DocumentTemplate]:
    """
    Retrieves all document templates.
    """
    return session.exec(select(DocumentTemplate)).all()

def get_template_id(session: Session, template_id: str) -> DocumentTemplate | None:
    """
    Retrieves a document template by its ID.
    """
    return session.get(DocumentTemplate, template_id)

def update_template(session: Session, template_id: str, data: DocumentTemplateUpdate) -> DocumentTemplate | None:
    """
    Updates an existing document template with the provided data.
    If the template does not exist, returns None.
    """
    template = session.get(DocumentTemplate, template_id)
    if not template:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template

def soft_delete_template(session: Session, template_id: str, reason: str) -> DocumentTemplate | None:
    """
    Soft deletes a document template by marking it as deleted and setting the reason.
    If the template does not exist, returns None.
    """
    template = session.get(DocumentTemplate, template_id)
    if not template or template.deleted:
        return None
    if template:
        template.deleted = True
        template.reason_for_delete = reason
        template.deleted_at = datetime.now(timezone.utc)
        session.add(template)
        session.commit()
    return template


def get_unit_templates(session: Session, unit_id: str) -> Sequence[DocumentTemplate]:
    """
    Retrieves all document templates associated with a specific unit.
    """
    return session.exec(select(DocumentTemplate).where(DocumentTemplate.unit_id == unit_id)).all()


# Signed Document
def create_signed_doc(session: Session, data: SignedDocumentCreate) -> SignedDocument:
    """
    Creates a new signed document record in the database.
    :param session: SQLAlchemy session object
    :param data: Data model containing the signed document details
    :return: The created SignedDocument object
    """
    record = SignedDocument(**data.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)

    if record.agent_id:

        create_notification(
            session,
            data={
                "user_id": record.agent_id,
                "title": "New Document Template Created",
                "body": f"Document '{record.name}' has been created.",
                "data": {
                    "template_id": record.id,
                    "type": "document_template_created"
                }
            }
        )
    
    if record.client_id:
        create_notification(
            session,
            data={
                "user_id": record.client_id,
                "title": "New Document Template Created",
                "body": f"Document '{record.name}' has been created.",
                "data": {
                    "template_id": record.id,
                    "type": "document_template_created"
                }
            }
        )


    return record


def get_all_signed_docs(session: Session) -> Sequence[SignedDocument]:
    """
    Retrieves all signed documents from the database.
    :param session: SQLAlchemy session object
    :return: List of SignedDocument objects
    """
    return session.exec(select(SignedDocument)).all()

def get_signed_template(session: Session, doc_id: str) -> DocumentTemplate | None:
    """
    Retrieves the document template associated with a signed document by its ID.
    :param session: SQLAlchemy session object
    :param doc_id: ID of the signed document
    :return: DocumentTemplate object if found, otherwise None
    """
    return session.exec(select(DocumentTemplate).where(SignedDocument.id == doc_id)).first()

def soft_delete_signed_doc(session: Session, doc_id: str, reason: str) -> SignedDocument | None:
    """
    Soft deletes a signed document by marking it as deleted and setting the reason.
    :param session: SQLAlchemy session object
    :param doc_id: ID of the signed document to be deleted
    :param reason: Reason for deletion
    :return: The updated SignedDocument object if found, otherwise None
    """
    signed_doc = session.get(SignedDocument, doc_id)
    if signed_doc:
        signed_doc.deleted = True
        signed_doc.reason_for_delete = reason
        signed_doc.deleted_at = datetime.now(timezone.utc)
        session.add(signed_doc)
        session.commit()
    return signed_doc


def get_signed_docs_for_unit(session: Session, unit_id: str) -> Sequence[SignedDocument]:
    """
    Retrieves all signed documents associated with a specific unit.
    :param session: SQLAlchemy session object
    :param unit_id: ID of the unit
    :return: List of SignedDocument objects associated with the unit
    """
    return session.exec(select(SignedDocument).where(SignedDocument.unit_id == unit_id)).all()


def get_signed_docs_for_client(session: Session, client_id: str) -> Sequence[SignedDocument]:
    """
    Retrieves all signed documents associated with a specific client.
    :param session: SQLAlchemy session object
    :param client_id: ID of the client
    :return: List of SignedDocument objects associated with the client
    """
    return session.exec(select(SignedDocument).where(SignedDocument.client_id == client_id)).all()


def get_signed_docs_for_agent(session: Session, agent_id: str) -> Sequence[SignedDocument]:
    """
    Retrieves all signed documents associated with a specific agent.
    :param session: SQLAlchemy session object
    :param agent_id: ID of the agent
    :return: List of SignedDocument objects associated with the agent
    """
    return session.exec(select(SignedDocument).where(SignedDocument.agent_id == agent_id)).all()