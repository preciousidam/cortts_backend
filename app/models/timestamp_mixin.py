from datetime import datetime, timezone
from sqlmodel import Field
from typing import Optional

class TimestampMixin:
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    deleted_at: Optional[datetime] = Field(
        default=None, nullable=True
    )