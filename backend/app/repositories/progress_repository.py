import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.models.master_code_letter import MasterCodeLetter
from app.models.player_achievement import PlayerAchievement
from app.models.player_master_code_letter import PlayerMasterCodeLetter


class ProgressRepository:
    """Read-only views of a player's overall progress across all quests."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_player_achievements(
        self, player_id: uuid.UUID
    ) -> list[tuple[Achievement, PlayerAchievement]]:
        result = await self.db.execute(
            select(Achievement, PlayerAchievement)
            .join(
                PlayerAchievement, PlayerAchievement.achievement_id == Achievement.id
            )
            .where(PlayerAchievement.player_id == player_id)
            .order_by(PlayerAchievement.earned_at)
        )
        return list(result.all())

    async def get_all_master_code_letters(self) -> list[MasterCodeLetter]:
        result = await self.db.execute(
            select(MasterCodeLetter).order_by(MasterCodeLetter.position)
        )
        return list(result.scalars().all())

    async def get_player_master_code_letter_ids(
        self, player_id: uuid.UUID
    ) -> set[uuid.UUID]:
        result = await self.db.execute(
            select(PlayerMasterCodeLetter.master_code_letter_id).where(
                PlayerMasterCodeLetter.player_id == player_id
            )
        )
        return set(result.scalars().all())
