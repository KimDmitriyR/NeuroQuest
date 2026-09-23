import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChoiceOutcome(str, enum.Enum):
    """Maps the ✅ / ⚠️ / ❌ marker used next to a choice's status in the source."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Choice(Base):
    """One of the options (A/B/C) a player can pick on a QuestNode.

    Carries the full narrative consequence, since in the source material the
    outcome (status + lesson + reward) belongs to the choice the player made,
    not to a separate node.
    """

    __tablename__ = "choices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quest_nodes.id"), nullable=False
    )

    # "A", "B", "C" label + the option text itself, e.g. "Занять у друзей"
    label: Mapped[str] = mapped_column(String(5), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # "Если A: Друзья дали денег, но..."
    consequence_text: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[ChoiceOutcome] = mapped_column(
        Enum(ChoiceOutcome, name="choice_outcome"), nullable=False
    )
    # "Статус: «Должник»"
    status_label: Mapped[str | None] = mapped_column(String(150), nullable=True)
    # "Урок: Занимать легко, отдавать сложно"
    lesson_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    achievement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=True
    )

    # "Доступ: Открыт раздел «Где искать подработку подростку»"
    unlock_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    unlock_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    next_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quest_nodes.id"), nullable=False
    )

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    node: Mapped["QuestNode"] = relationship(
        "QuestNode", foreign_keys=[node_id], back_populates="choices"
    )
