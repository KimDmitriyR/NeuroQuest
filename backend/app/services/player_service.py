import uuid

from app.core.security import create_player_token
from app.models.player import Player
from app.repositories.player_repository import PlayerRepository


class PlayerNotFoundError(Exception):
    pass


class PlayerService:
    """Owns player-related business rules (currently minimal)."""

    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    async def create_player(self, name: str, parent_id: uuid.UUID) -> Player:
        return await self.repository.create(name=name, parent_id=parent_id)

    async def get_player(self, player_id: uuid.UUID) -> Player:
        player = await self.repository.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(player_id)
        return player

    def issue_token(self, player: Player) -> str:
        return create_player_token(player.id, player.token_version)

    async def reset_token(self, player: Player) -> str:
        """Invalidate old links/devices and hand out a fresh token."""
        player = await self.repository.bump_token_version(player)
        return self.issue_token(player)
