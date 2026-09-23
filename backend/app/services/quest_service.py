import uuid
from dataclasses import dataclass

from app.models.achievement import Achievement
from app.models.choice import Choice
from app.models.master_code_letter import MasterCodeLetter
from app.models.quest_node import QuestNode, QuestNodeType
from app.models.quest_session import QuestSession, QuestSessionStatus
from app.repositories.quest_repository import QuestRepository
from app.repositories.quest_session_repository import QuestSessionRepository


class QuestCardNotFoundError(Exception):
    pass


class QuestSessionNotFoundError(Exception):
    pass


class InvalidChoiceError(Exception):
    """Raised when a choice doesn't belong to the session's current node,
    or the session is already completed."""


@dataclass
class ChoiceResult:
    session: QuestSession
    chosen: Choice
    achievement_granted: Achievement | None
    completed: bool
    completion_achievement: Achievement | None
    master_code_letter: MasterCodeLetter | None
    next_node: QuestNode | None  # None when completed


class QuestService:
    """Owns the rules of moving a player through a quest's graph."""

    def __init__(
        self, quest_repo: QuestRepository, session_repo: QuestSessionRepository
    ):
        self.quest_repo = quest_repo
        self.session_repo = session_repo

    async def start_quest(self, player_id: uuid.UUID, qr_token: str) -> QuestSession:
        card = await self.quest_repo.get_card_by_qr_token(qr_token)
        if card is None:
            raise QuestCardNotFoundError(qr_token)

        existing = await self.session_repo.get_active_session(player_id, card.quest_id)
        if existing is not None:
            return existing

        quest = await self.quest_repo.get_quest(card.quest_id)
        session = await self.session_repo.create(
            player_id=player_id,
            quest_id=quest.id,
            start_node_id=quest.start_node_id,
        )
        await self.session_repo.db.commit()
        return session

    async def get_session(self, session_id: uuid.UUID) -> QuestSession:
        session = await self.session_repo.get_by_id(session_id)
        if session is None:
            raise QuestSessionNotFoundError(session_id)
        return session

    async def get_current_node(self, session: QuestSession) -> QuestNode:
        node = await self.quest_repo.get_node_with_choices(session.current_node_id)
        return node

    async def submit_choice(
        self, session: QuestSession, choice_id: uuid.UUID
    ) -> ChoiceResult:
        if session.status == QuestSessionStatus.COMPLETED:
            raise InvalidChoiceError("session already completed")

        choice = await self.quest_repo.get_choice(choice_id)
        if choice is None or choice.node_id != session.current_node_id:
            raise InvalidChoiceError("choice does not belong to the current node")

        await self.session_repo.record_answer(
            session, node_id=session.current_node_id, choice_id=choice.id
        )

        achievement_granted: Achievement | None = None
        if choice.achievement_id is not None:
            newly = await self.session_repo.grant_achievement(
                session.player_id, choice.achievement_id
            )
            if newly:
                achievement_granted = await self.quest_repo.get_achievement(
                    choice.achievement_id
                )

        next_node = await self.quest_repo.get_node_with_choices(choice.next_node_id)
        await self.session_repo.advance(session, next_node.id)

        completion_achievement: Achievement | None = None
        master_code_letter: MasterCodeLetter | None = None
        completed = next_node.type == QuestNodeType.COMPLETION

        if completed:
            await self.session_repo.complete(session)

            if next_node.achievement_id is not None:
                newly = await self.session_repo.grant_achievement(
                    session.player_id, next_node.achievement_id
                )
                if newly:
                    completion_achievement = await self.quest_repo.get_achievement(
                        next_node.achievement_id
                    )

            card = await self.quest_repo.get_card_by_quest_id(session.quest_id)
            letter = await self.quest_repo.get_master_code_letter_by_card(card.id)
            if letter is not None:
                newly = await self.session_repo.grant_master_code_letter(
                    session.player_id, letter.id
                )
                if newly:
                    master_code_letter = letter

        await self.session_repo.db.commit()

        return ChoiceResult(
            session=session,
            chosen=choice,
            achievement_granted=achievement_granted,
            completed=completed,
            completion_achievement=completion_achievement,
            master_code_letter=master_code_letter,
            next_node=None if completed else next_node,
        )
