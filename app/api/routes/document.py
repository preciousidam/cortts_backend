from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.document import (
    DocumentTemplateCreate, DocumentTemplateRead,
    SignedDocumentCreate, SignedDocumentRead
)
from app.services.document_service import (
    create_template, get_unit_templates,
    create_signed_doc, get_signed_docs_for_unit,
    get_signed_docs_for_client, get_signed_docs_for_agent
)
from app.auth.dependencies import get_current_user
from app.models.user import Role
router = APIRouter()


# Templates
@router.post("/templates", response_model=DocumentTemplateRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create_doc_template(data: DocumentTemplateCreate, session: Session = Depends(get_session)):
    return create_template(session, data)


@router.get("/templates/unit/{unit_id}", response_model=list[DocumentTemplateRead], dependencies=[Depends(get_current_user([Role.ADMIN]))])
def list_templates_by_unit(unit_id: str, session: Session = Depends(get_session)):
    return get_unit_templates(session, unit_id)


# Signed Docs
@router.post("/signed", response_model=SignedDocumentRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def upload_signed_doc(data: SignedDocumentCreate, session: Session = Depends(get_session)):
    return create_signed_doc(session, data)


@router.get("/signed/unit/{unit_id}", response_model=list[SignedDocumentRead], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def signed_docs_by_unit(unit_id: str, session: Session = Depends(get_session)):
    return get_signed_docs_for_unit(session, unit_id)


@router.get("/signed/client/{client_id}", response_model=list[SignedDocumentRead], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def signed_docs_by_client(client_id: str, session: Session = Depends(get_session)):
    return get_signed_docs_for_client(session, client_id)


@router.get("/signed/agent/{agent_id}", response_model=list[SignedDocumentRead], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def signed_docs_by_agent(agent_id: str, session: Session = Depends(get_session)):
    return get_signed_docs_for_agent(session, agent_id)