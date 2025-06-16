from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional


# Document Template
class DocumentTemplateBase(SQLModel):
    name: str
    link: str
    unit_id: str


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateRead(DocumentTemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime


# Signed Document
class SignedDocumentBase(SQLModel):
    name: str
    link: str
    unit_id: str
    client_id: Optional[str] = None
    agent_id: Optional[str] = None


class SignedDocumentCreate(SignedDocumentBase):
    pass


class SignedDocumentRead(SignedDocumentBase):
    id: str
    created_at: datetime
    updated_at: datetime