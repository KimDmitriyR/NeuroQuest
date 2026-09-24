import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.mission_repository import MissionRepository
from app.repositories.quest_session_repository import QuestSessionRepository
from app.schemas.mission import (
    AttemptView,
    MissionView,
    ReviewAttemptRequest,
    StartAttemptRequest,
    SubmitAttemptRequest,
)
from app.services.mission_service import (
    AttemptNotFoundError,
    InvalidAttemptStateError,
    MissionNotFoundError,
    MissionService,
)

router = APIRouter(prefix="/api/missions", tags=["missions"])


def get_mission_service(db: AsyncSession = Depends(get_db)) -> MissionService:
    return MissionService(MissionRepository(db), QuestSessionRepository(db))


async def _get_attempt_or_404(service: MissionService, attempt_id: uuid.UUID):
    attempt = await service.mission_repo.get_attempt(attempt_id)
    if attempt is None:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt


@router.get("/{mission_id}", response_model=MissionView)
async def get_mission(
    mission_id: uuid.UUID,
    service: MissionService = Depends(get_mission_service),
) -> MissionView:
    mission = await service.mission_repo.get_mission(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionView.model_validate(mission)


@router.post("/{mission_id}/attempts", response_model=AttemptView, status_code=201)
async def start_attempt(
    mission_id: uuid.UUID,
    payload: StartAttemptRequest,
    service: MissionService = Depends(get_mission_service),
) -> AttemptView:
    try:
        attempt = await service.start_attempt(payload.player_id, mission_id)
    except MissionNotFoundError:
        raise HTTPException(status_code=404, detail="Mission not found")
    return AttemptView.model_validate(attempt)


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptView)
async def submit_attempt(
    attempt_id: uuid.UUID,
    payload: SubmitAttemptRequest,
    service: MissionService = Depends(get_mission_service),
) -> AttemptView:
    attempt = await _get_attempt_or_404(service, attempt_id)
    try:
        attempt = await service.submit_attempt(
            attempt, payload.photo_url, payload.text_answer
        )
    except InvalidAttemptStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return AttemptView.model_validate(attempt)


@router.post("/attempts/{attempt_id}/review", response_model=AttemptView)
async def review_attempt(
    attempt_id: uuid.UUID,
    payload: ReviewAttemptRequest,
    service: MissionService = Depends(get_mission_service),
) -> AttemptView:
    # NOTE: unauthenticated for now, like the rest of the API - this should
    # move behind a moderator/parent role once auth exists (see plan).
    attempt = await _get_attempt_or_404(service, attempt_id)
    try:
        attempt = await service.review_attempt(attempt, payload.approved)
    except InvalidAttemptStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return AttemptView.model_validate(attempt)
