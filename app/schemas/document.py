from unittest.mock import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum
from app.schemas.media import MediaFileReadSchema
from app.schemas.unit import UnitRead  # Assuming UnitReadSchema is defined elsewhere


# Document Template
class DocumentTemplateBase(BaseModel):
    name: str
    media_file_id: UUID
    unit_id: UUID
    deleted_at: Optional[bool] = False


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateRead(DocumentTemplateBase):
    id: UUID
    media_file: MediaFileReadSchema
    unit: UnitRead
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
    unit_id: UUID
    client_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None


class SignedDocumentCreate(SignedDocumentBase):
    pass


class SignedDocumentRead(SignedDocumentBase):
    id: UUID
    media_file: MediaFileReadSchema
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


class DocumentKind(str, Enum):
    TEMPLATE = "template"
    SIGNED = "signed"

class DocumentRead(BaseModel):
    id: UUID
    name: str
    unit_id: UUID
    kind: DocumentKind
    created_at: datetime | None = None
    media_file: MediaFileReadSchema | None = None  # includes file_path, file_type, etc.

    model_config = {
        "from_attributes": True,
    }

class ReadAllDocuments(BaseModel):
    data: list[DocumentRead]
    count: int