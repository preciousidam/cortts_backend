from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.document import (
    DocumentTemplateCreate, DocumentTemplateRead,
    SignedDocumentCreate, SignedDocumentRead
)
from app.services.document_service import (
    create_template, get_unit_templates,
    create_signed_doc, get_signed_docs_for_unit,
    get_signed_docs_for_client, get_signed_docs_for_agent, get_templates,
    get_template_id, soft_delete_signed_doc, soft_delete_template
)
from app.auth.dependencies import get_current_user
from app.models.user import Role
router = APIRouter()


# Templates
@router.post("/templates", response_model=DocumentTemplateRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create_doc_template(data: DocumentTemplateCreate, session: Session = Depends(get_session)):
    """
    Create a new document template.
    """

    media = create_template(session, data)
    if not media:
        raise HTTPException(status_code=400, detail="Failed to create document template")  

    return media

@router.get("/templates", response_model=list[DocumentTemplateRead], dependencies=[Depends(get_current_user([Role.ADMIN]))])
def list_templates(session: Session = Depends(get_session)):
    return get_templates(session)

@router.get("/templates/{template_id}", response_model=DocumentTemplateRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def get_template_by_id(template_id: str, session: Session = Depends(get_session)):
    return get_template_id(session, template_id)


@router.get("/templates/unit/{unit_id}", response_model=list[DocumentTemplateRead], dependencies=[Depends(get_current_user([Role.ADMIN]))])
def list_templates_by_unit(unit_id: str, session: Session = Depends(get_session)):
    return get_unit_templates(session, unit_id)

@router.delete("/templates/{template_id}", dependencies=[Depends(get_current_user([Role.ADMIN]))])
def delete_template(template_id: str, reason: str, session: Session = Depends(get_session)):
    """
    Soft delete a document template by ID.
    """
    return soft_delete_template(session, template_id, reason)


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

@router.delete("/signed/{doc_id}", dependencies=[Depends(get_current_user([Role.ADMIN]))])
def delete_signed_doc(doc_id: str, reason: str, session: Session = Depends(get_session)):
    return soft_delete_signed_doc(session, doc_id, reason)
