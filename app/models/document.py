from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.models.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from app.models.unit import Unit
    from app.models.user import User
    from app.models.project import Project

class MediaFile(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    file_type: str
    file_name: str
    file_path: str
    file_size: int
    unit_id: Optional[UUID] = Field(default=None, foreign_key="unit.id")
    unit: Optional["Unit"] = Relationship(back_populates="media_files")
    project_id: Optional[UUID] = Field(default=None, foreign_key="project.id")
    project: Optional["Project"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    deleted: bool = False
    uploaded_by: Optional[UUID] = Field(default=None, foreign_key="user.id")
    uploader: Optional["User"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )

class DocumentTemplate(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    media_file_id: UUID = Field(foreign_key="mediafile.id")
    unit_id: UUID = Field(foreign_key="unit.id")
    deleted: bool = False
    reason_for_delete: Optional[str] = None
    media_file: Optional[MediaFile] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    unit: Optional["Unit"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )


class SignedDocument(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    media_file_id: UUID = Field(foreign_key="mediafile.id")
    unit_id: UUID = Field(foreign_key="unit.id")
    client_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    agent_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    deleted: bool = False
    reason_for_delete: Optional[str] = None
    media_file: Optional[MediaFile] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    unit: Optional["Unit"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
