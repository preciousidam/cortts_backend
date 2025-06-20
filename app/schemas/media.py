from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserRead

class MediaFileBaseSchema(BaseModel):
    file_type: str
    file_name: str
    file_path: str
    file_size: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    uploaded_by: UUID | None = None
    uploader: UserRead | None = None

class MediaFileCreateSchema(MediaFileBaseSchema):
    pass

class MediaFileReadSchema(MediaFileBaseSchema):
    id: UUID