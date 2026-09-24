import uuid
from datetime import datetime, timezone

from app.models.envelope_mission import ValidationType
from app.models.mission_attempt import MissionAttempt, MissionAttemptStatus
from app.repositories.mission_repository import MissionRepository
from app.repositories.quest_session_repository import QuestSessionRepository


class MissionNotFoundError(Exception):
    pass


class AttemptNotFoundError(Exception):
    pass


class InvalidAttemptStateError(Exception):
    pass


class MissionService:
    def __init__(
        self,
        mission_repo: MissionRepository,
        session_repo: QuestSessionRepository,
    ):
        self.mission_repo = mission_repo
        # reused only for its idempotent grant_achievement() helper - a
        # player's achievements are one shared collection, not owned by
        # quests specifically
        self.session_repo = session_repo

    async def start_attempt(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> MissionAttempt:
        mission = await self.mission_repo.get_mission(mission_id)
        if mission is None:
            raise MissionNotFoundError(mission_id)

        existing = await self.mission_repo.get_active_attempt(player_id, mission_id)
        if existing is not None:
            return existing

        attempt = await self.mission_repo.create_attempt(player_id, mission_id)
        await self.mission_repo.db.commit()
        return attempt

    async def submit_attempt(
        self,
        attempt: MissionAttempt,
        photo_url: str | None,
        text_answer: str | None,
    ) -> MissionAttempt:
        if attempt.status != MissionAttemptStatus.IN_PROGRESS:
            raise InvalidAttemptStateError("attempt is not in progress")

        mission = await self.mission_repo.get_mission(attempt.mission_id)
        attempt.photo_url = photo_url
        attempt.text_answer = text_answer
        attempt.submitted_at = datetime.now(timezone.utc)

        if mission.validation_type == ValidationType.TEXT:
            expected = (mission.validation_config or {}).get("answer", "")
            is_correct = (
                text_answer is not None
                and text_answer.strip().lower() == expected.strip().lower()
            )
            attempt.status = (
                MissionAttemptStatus.APPROVED
                if is_correct
                else MissionAttemptStatus.REJECTED
            )
            if is_correct:
                await self._grant_reward(attempt, mission)
                attempt.completed_at = datetime.now(timezone.utc)
        else:
            # photo missions can't be auto-checked (no CV in the MVP) -
            # always needs a manual review via review_attempt()
            attempt.status = MissionAttemptStatus.SUBMITTED

        await self.mission_repo.db.commit()
        return attempt

    async def review_attempt(
        self, attempt: MissionAttempt, approved: bool
    ) -> MissionAttempt:
        if attempt.status != MissionAttemptStatus.SUBMITTED:
            raise InvalidAttemptStateError("attempt is not awaiting review")

        mission = await self.mission_repo.get_mission(attempt.mission_id)
        attempt.status = (
            MissionAttemptStatus.APPROVED if approved else MissionAttemptStatus.REJECTED
        )
        attempt.completed_at = datetime.now(timezone.utc)

        if approved:
            await self._grant_reward(attempt, mission)

        await self.mission_repo.db.commit()
        return attempt

    async def _grant_reward(self, attempt: MissionAttempt, mission) -> None:
        await self.session_repo.grant_achievement(
            attempt.player_id, mission.achievement_id
        )
