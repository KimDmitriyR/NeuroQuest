import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuestCard(Base):
    """The physical card a player scans (QR) to start a Quest."""

    __tablename__ = "quest_cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=False
    )
    quest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False, unique=True
    )

    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    # "Сюжет": the intro text printed on the physical card
    intro_text: Mapped[str] = mapped_column(Text, nullable=False)

    # scanned QR payload -> used to look the card up without exposing the DB id
    qr_token: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
