from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from uuid import UUID


# Document Template
class DocumentTemplateBase(SQLModel):
    name: str
    link: str
    unit_id: UUID


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateRead(DocumentTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# Signed Document
class SignedDocumentBase(SQLModel):
    name: str
    link: str
    unit_id: UUID
    client_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None


class SignedDocumentCreate(SignedDocumentBase):
    pass


class SignedDocumentRead(SignedDocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime