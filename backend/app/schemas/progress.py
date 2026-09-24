from datetime import datetime

from pydantic import BaseModel


class EarnedAchievementView(BaseModel):
    title: str
    description: str | None
    is_badge: bool
    earned_at: datetime


class MasterCodeSlotView(BaseModel):
    position: int
    letter: str | None
    unlocked: bool


class MasterCodeProgressView(BaseModel):
    slots: list[MasterCodeSlotView]
    total_positions: int
    unlocked_count: int
    is_complete: bool
