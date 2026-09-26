import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MissionAttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"  # photo-type missions land here, awaiting review
    APPROVED = "approved"
    REJECTED = "rejected"


class MissionAttempt(Base):
    """One player's attempt at one EnvelopeMission."""

    __tablename__ = "mission_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id"), nullable=False
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("envelope_missions.id"), nullable=False
    )
    status: Mapped[MissionAttemptStatus] = mapped_column(
        Enum(MissionAttemptStatus, name="mission_attempt_status"),
        nullable=False,
        default=MissionAttemptStatus.IN_PROGRESS,
    )
    # for multi-step TEXT missions (validation_config -> {"steps": [...]}):
    # how many steps have been solved correctly so far
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    text_answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
