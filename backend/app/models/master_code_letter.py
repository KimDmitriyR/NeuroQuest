import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MasterCodeLetter(Base):
    """One letter of the master-code phrase, unlocked by completing a card.

    The phrase itself ("ТВОЙ НОВЫЙ КОД") is game content, not hardcoded here:
    each row just says which letter sits at which position, and which card
    unlocks it.
    """

    __tablename__ = "master_code_letters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quest_card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quest_cards.id"), nullable=False, unique=True
    )
    letter: Mapped[str] = mapped_column(String(2), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
