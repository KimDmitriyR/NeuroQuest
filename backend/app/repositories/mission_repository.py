import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.envelope_mission import EnvelopeMission
from app.models.mission_attempt import MissionAttempt, MissionAttemptStatus


class MissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_mission(self, mission_id: uuid.UUID) -> EnvelopeMission | None:
        result = await self.db.execute(
            select(EnvelopeMission).where(EnvelopeMission.id == mission_id)
        )
        return result.scalar_one_or_none()

    async def list_missions(self) -> list[EnvelopeMission]:
        result = await self.db.execute(
            select(EnvelopeMission)
            .where(EnvelopeMission.is_active.is_(True))
            .order_by(EnvelopeMission.sort_order)
        )
        return list(result.scalars().all())

    async def get_attempt(self, attempt_id: uuid.UUID) -> MissionAttempt | None:
        result = await self.db.execute(
            select(MissionAttempt).where(MissionAttempt.id == attempt_id)
        )
        return result.scalar_one_or_none()

    async def get_active_attempt(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> MissionAttempt | None:
        result = await self.db.execute(
            select(MissionAttempt).where(
                MissionAttempt.player_id == player_id,
                MissionAttempt.mission_id == mission_id,
                MissionAttempt.status.in_(
                    [MissionAttemptStatus.IN_PROGRESS, MissionAttemptStatus.SUBMITTED]
                ),
            )
        )
        return result.scalar_one_or_none()

    async def create_attempt(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> MissionAttempt:
        attempt = MissionAttempt(player_id=player_id, mission_id=mission_id)
        self.db.add(attempt)
        await self.db.flush()
        return attempt
