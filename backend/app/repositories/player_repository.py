import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player


class PlayerRepository:
    """Data access for Player. Knows nothing about game rules."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, player_id: uuid.UUID) -> Player | None:
        result = await self.db.execute(select(Player).where(Player.id == player_id))
        return result.scalar_one_or_none()

    async def create(self, name: str) -> Player:
        player = Player(name=name)
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player
