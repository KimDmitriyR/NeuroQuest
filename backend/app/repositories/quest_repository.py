import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.achievement import Achievement
from app.models.choice import Choice
from app.models.master_code_letter import MasterCodeLetter
from app.models.quest import Quest
from app.models.quest_card import QuestCard
from app.models.quest_node import QuestNode


class QuestRepository:
    """Read access to quest content: cards, the graph of nodes/choices."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_card_by_qr_token(self, qr_token: str) -> QuestCard | None:
        result = await self.db.execute(
            select(QuestCard).where(QuestCard.qr_token == qr_token)
        )
        return result.scalar_one_or_none()

    async def get_quest(self, quest_id: uuid.UUID) -> Quest | None:
        result = await self.db.execute(select(Quest).where(Quest.id == quest_id))
        return result.scalar_one_or_none()

    async def get_node_with_choices(self, node_id: uuid.UUID) -> QuestNode | None:
        result = await self.db.execute(
            select(QuestNode)
            .where(QuestNode.id == node_id)
            .options(selectinload(QuestNode.choices))
        )
        return result.scalar_one_or_none()

    async def get_choice(self, choice_id: uuid.UUID) -> Choice | None:
        result = await self.db.execute(select(Choice).where(Choice.id == choice_id))
        return result.scalar_one_or_none()

    async def get_achievement(self, achievement_id: uuid.UUID) -> Achievement | None:
        result = await self.db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        return result.scalar_one_or_none()

    async def get_master_code_letter_by_card(
        self, quest_card_id: uuid.UUID
    ) -> MasterCodeLetter | None:
        result = await self.db.execute(
            select(MasterCodeLetter).where(
                MasterCodeLetter.quest_card_id == quest_card_id
            )
        )
        return result.scalar_one_or_none()

    async def get_card_by_quest_id(self, quest_id: uuid.UUID) -> QuestCard | None:
        result = await self.db.execute(
            select(QuestCard).where(QuestCard.quest_id == quest_id)
        )
        return result.scalar_one_or_none()
