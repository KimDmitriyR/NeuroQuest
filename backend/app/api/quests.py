import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.quest_repository import QuestRepository
from app.repositories.quest_session_repository import QuestSessionRepository
from app.schemas.quest import (
    AchievementView,
    ChoiceResultView,
    MasterCodeLetterView,
    NodeView,
    SessionView,
    StartQuestRequest,
    SubmitChoiceRequest,
)
from app.services.quest_service import (
    InvalidChoiceError,
    QuestCardNotFoundError,
    QuestService,
    QuestSessionNotFoundError,
)

router = APIRouter(prefix="/api/quests", tags=["quests"])


def get_quest_service(db: AsyncSession = Depends(get_db)) -> QuestService:
    return QuestService(QuestRepository(db), QuestSessionRepository(db))


async def _session_view(service: QuestService, session) -> SessionView:
    node = await service.get_current_node(session)
    return SessionView(
        id=session.id,
        player_id=session.player_id,
        quest_id=session.quest_id,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        current_node=NodeView.model_validate(node),
    )


@router.post("/start", response_model=SessionView, status_code=201)
async def start_quest(
    payload: StartQuestRequest,
    service: QuestService = Depends(get_quest_service),
) -> SessionView:
    try:
        session = await service.start_quest(payload.player_id, payload.qr_token)
    except QuestCardNotFoundError:
        raise HTTPException(status_code=404, detail="Quest card not found")
    return await _session_view(service, session)


@router.get("/sessions/{session_id}", response_model=SessionView)
async def get_session(
    session_id: uuid.UUID,
    service: QuestService = Depends(get_quest_service),
) -> SessionView:
    try:
        session = await service.get_session(session_id)
    except QuestSessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    return await _session_view(service, session)


@router.post("/sessions/{session_id}/choices", response_model=ChoiceResultView)
async def submit_choice(
    session_id: uuid.UUID,
    payload: SubmitChoiceRequest,
    service: QuestService = Depends(get_quest_service),
) -> ChoiceResultView:
    try:
        session = await service.get_session(session_id)
    except QuestSessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        result = await service.submit_choice(session, payload.choice_id)
    except InvalidChoiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ChoiceResultView(
        status_label=result.chosen.status_label,
        outcome=result.chosen.outcome,
        consequence_text=result.chosen.consequence_text,
        lesson_text=result.chosen.lesson_text,
        unlock_title=result.chosen.unlock_title,
        unlock_description=result.chosen.unlock_description,
        achievement_granted=(
            AchievementView.model_validate(result.achievement_granted)
            if result.achievement_granted
            else None
        ),
        completed=result.completed,
        completion_achievement=(
            AchievementView.model_validate(result.completion_achievement)
            if result.completion_achievement
            else None
        ),
        master_code_letter=(
            MasterCodeLetterView.model_validate(result.master_code_letter)
            if result.master_code_letter
            else None
        ),
        next_node=(
            NodeView.model_validate(result.next_node) if result.next_node else None
        ),
    )
