import uuid

from app.models.player import Player
from app.repositories.player_repository import PlayerRepository


class PlayerNotFoundError(Exception):
    pass


class PlayerService:
    """Owns player-related business rules (currently minimal)."""

    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    async def create_player(self, name: str) -> Player:
        return await self.repository.create(name=name)

    async def get_player(self, player_id: uuid.UUID) -> Player:
        player = await self.repository.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(player_id)
        return player
