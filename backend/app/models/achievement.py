import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Achievement(Base):
    """Catalog of achievements a player can earn.

    Two granularities appear in the real content: small per-stage
    achievements, and a bigger per-card badge (`is_badge=True`) awarded on
    quest completion. Both are the same entity — the source material never
    used a separate 'Skill' concept, so we don't invent one.
    """

    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_badge: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
