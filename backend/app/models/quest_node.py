import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QuestNodeType(str, enum.Enum):
    # bot asks a question, player must pick one of the node's choices
    CHOICE = "choice"
    # terminal node reached when the player finishes the whole card
    COMPLETION = "completion"


class QuestNode(Base):
    """A single step in a quest's graph (a 🤖 Бот question + its choices)."""

    __tablename__ = "quest_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False
    )
    type: Mapped[QuestNodeType] = mapped_column(
        Enum(QuestNodeType, name="quest_node_type"), nullable=False
    )

    # bot's message shown to the player at this step ("🤖 Бот: ...")
    message: Mapped[str] = mapped_column(Text, nullable=False)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Reward granted unconditionally on reaching a COMPLETION node (the
    # source material awards the card-final badge/unlock regardless of which
    # A/B/C path the player took through the earlier stages).
    achievement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", name="fk_quest_nodes_achievement_id_achievements"),
        nullable=True,
    )
    unlock_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    unlock_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    choices: Mapped[list["Choice"]] = relationship(
        "Choice",
        foreign_keys="Choice.node_id",
        back_populates="node",
        order_by="Choice.sort_order",
    )
