import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_achievement import PlayerAchievement
from app.models.player_master_code_letter import PlayerMasterCodeLetter
from app.models.quest_answer import QuestAnswer
from app.models.quest_session import QuestSession, QuestSessionStatus


class QuestSessionRepository:
    """Data access for a player's progress through a quest, and rewards earned."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, session_id: uuid.UUID) -> QuestSession | None:
        result = await self.db.execute(
            select(QuestSession).where(QuestSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_active_session(
        self, player_id: uuid.UUID, quest_id: uuid.UUID
    ) -> QuestSession | None:
        result = await self.db.execute(
            select(QuestSession).where(
                QuestSession.player_id == player_id,
                QuestSession.quest_id == quest_id,
                QuestSession.status == QuestSessionStatus.IN_PROGRESS,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self, player_id: uuid.UUID, quest_id: uuid.UUID, start_node_id: uuid.UUID
    ) -> QuestSession:
        session = QuestSession(
            player_id=player_id, quest_id=quest_id, current_node_id=start_node_id
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def record_answer(
        self, session: QuestSession, node_id: uuid.UUID, choice_id: uuid.UUID
    ) -> None:
        self.db.add(
            QuestAnswer(session_id=session.id, node_id=node_id, choice_id=choice_id)
        )

    async def advance(self, session: QuestSession, next_node_id: uuid.UUID) -> None:
        session.current_node_id = next_node_id

    async def complete(self, session: QuestSession) -> None:
        session.status = QuestSessionStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)

    async def grant_achievement(
        self, player_id: uuid.UUID, achievement_id: uuid.UUID
    ) -> bool:
        """Returns True if newly granted, False if the player already had it."""
        existing = await self.db.execute(
            select(PlayerAchievement).where(
                PlayerAchievement.player_id == player_id,
                PlayerAchievement.achievement_id == achievement_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            return False
        self.db.add(
            PlayerAchievement(player_id=player_id, achievement_id=achievement_id)
        )
        return True

    async def grant_master_code_letter(
        self, player_id: uuid.UUID, letter_id: uuid.UUID
    ) -> bool:
        existing = await self.db.execute(
            select(PlayerMasterCodeLetter).where(
                PlayerMasterCodeLetter.player_id == player_id,
                PlayerMasterCodeLetter.master_code_letter_id == letter_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            return False
        self.db.add(
            PlayerMasterCodeLetter(
                player_id=player_id, master_code_letter_id=letter_id
            )
        )
        return True
