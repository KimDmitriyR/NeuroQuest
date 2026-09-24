import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ValidationType(str, enum.Enum):
    # a photo the player submits; nothing here can be auto-checked (no CV in
    # the MVP), so it always ends up needing a manual approve/reject
    PHOTO = "photo"
    # a text answer that's compared against validation_config directly
    TEXT = "text"


class EnvelopeMission(Base):
    """A physical mission from an envelope (not a QuestNode - see model docs:
    this is 'do a physical task, then submit proof', not 'read and choose')."""

    __tablename__ = "envelope_missions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # human-readable for now (e.g. "sector fully completed"); no gating logic
    # is enforced yet since the source material doesn't spell out a concrete
    # rule per mission
    unlock_condition: Mapped[str | None] = mapped_column(Text, nullable=True)

    validation_type: Mapped[ValidationType] = mapped_column(
        Enum(ValidationType, name="mission_validation_type"), nullable=False
    )
    # for TEXT: {"answer": "..."} (case-insensitive exact match)
    validation_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
