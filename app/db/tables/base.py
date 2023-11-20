from datetime import datetime
from uuid import uuid4

from sqlalchemy import text
from sqlmodel import Field, SQLModel
from pydantic import UUID4

class TimestampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )


class UUIDModel(SQLModel):
    id: UUID4 = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
