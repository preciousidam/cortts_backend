from datetime import datetime, timezone
from typing import Any, Optional, Type, cast
from sqlalchemy import DateTime
from sqlmodel import Field

class TimestampMixin:
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=cast(Type[Any], DateTime(timezone=True)),
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=cast(Type[Any], DateTime(timezone=True)),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_type=cast(Type[Any], DateTime(timezone=True)),
    )