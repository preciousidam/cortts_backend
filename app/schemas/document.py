from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.schemas.media import MediaFileReadSchema
from app.schemas.unit import UnitRead  # Assuming UnitReadSchema is defined elsewhere


# Document Template
class DocumentTemplateBase(BaseModel):
    name: str
    media_file_id: UUID
    media_file: MediaFileReadSchema
    unit_id: UUID
    deleted_at: Optional[bool] = False
    unit: UnitRead # Assuming UnitReadSchema is defined elsewhere


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateRead(DocumentTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class DocumentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    media_file_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    deleted_at: Optional[bool] = None
    reason_for_delete: Optional[str] = None


# Signed Document
class SignedDocumentBase(BaseModel):
    name: str
    media_file_id: UUID
    media_file: MediaFileReadSchema
    unit_id: UUID
    client_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None


class SignedDocumentCreate(SignedDocumentBase):
    pass


class SignedDocumentRead(SignedDocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class SignedDocumentUpdate(BaseModel):
    name: Optional[str] = None
    media_file_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    deleted_at: Optional[bool] = None
    reason_for_delete: Optional[str] = None