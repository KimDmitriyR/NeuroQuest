import uuid
from dataclasses import dataclass
from datetime import datetime

from app.models.achievement import Achievement
from app.repositories.player_repository import PlayerRepository
from app.repositories.progress_repository import ProgressRepository


class PlayerNotFoundError(Exception):
    pass


@dataclass
class EarnedAchievement:
    achievement: Achievement
    earned_at: datetime


@dataclass
class MasterCodeSlot:
    position: int
    letter: str | None  # None if the player hasn't unlocked this letter yet
    unlocked: bool


@dataclass
class MasterCodeProgress:
    slots: list[MasterCodeSlot]
    total_positions: int
    unlocked_count: int
    is_complete: bool


class ProgressService:
    def __init__(self, player_repo: PlayerRepository, progress_repo: ProgressRepository):
        self.player_repo = player_repo
        self.progress_repo = progress_repo

    async def _ensure_player_exists(self, player_id: uuid.UUID) -> None:
        player = await self.player_repo.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(player_id)

    async def get_achievements(self, player_id: uuid.UUID) -> list[EarnedAchievement]:
        await self._ensure_player_exists(player_id)
        rows = await self.progress_repo.get_player_achievements(player_id)
        return [
            EarnedAchievement(achievement=achievement, earned_at=link.earned_at)
            for achievement, link in rows
        ]

    async def get_master_code(self, player_id: uuid.UUID) -> MasterCodeProgress:
        await self._ensure_player_exists(player_id)
        all_letters = await self.progress_repo.get_all_master_code_letters()
        owned_ids = await self.progress_repo.get_player_master_code_letter_ids(
            player_id
        )

        slots = [
            MasterCodeSlot(
                position=letter.position,
                letter=letter.letter if letter.id in owned_ids else None,
                unlocked=letter.id in owned_ids,
            )
            for letter in all_letters
        ]
        unlocked_count = sum(1 for slot in slots if slot.unlocked)

        return MasterCodeProgress(
            slots=slots,
            total_positions=len(slots),
            unlocked_count=unlocked_count,
            is_complete=len(slots) > 0 and unlocked_count == len(slots),
        )
