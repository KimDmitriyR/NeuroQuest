import uuid

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sector(Base):
    """A colored section of the game (e.g. 'Финстартап 2.0').

    Color is stored as data, not hardcoded in the frontend, per the
    project's game-design rules (Sector -> color -> cards of that sector).
    """

    __tablename__ = "sectors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    color: Mapped[str] = mapped_column(String(50), nullable=False)
    color_token: Mapped[str] = mapped_column(String(50), nullable=False)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
