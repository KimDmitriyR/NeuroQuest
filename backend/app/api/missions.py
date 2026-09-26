import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.mission_repository import MissionRepository
from app.repositories.quest_session_repository import QuestSessionRepository
from app.schemas.mission import (
    AttemptView,
    MissionView,
    PendingAttemptView,
    ReviewAttemptRequest,
    StartAttemptRequest,
    SubmitAttemptRequest,
    SubmitAttemptResultView,
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


@router.get("", response_model=list[MissionView])
async def list_missions(
    service: MissionService = Depends(get_mission_service),
) -> list[MissionView]:
    missions = await service.mission_repo.list_missions()
    return [MissionView.model_validate(m) for m in missions]


@router.get("/attempts/pending", response_model=list[PendingAttemptView])
async def list_pending_attempts(
    service: MissionService = Depends(get_mission_service),
) -> list[PendingAttemptView]:
    # NOTE: unauthenticated for now, like the review endpoint below - this
    # is a moderator/parent view and should move behind that role once
    # auth exists (see plan).
    rows = await service.mission_repo.list_pending_attempts()
    return [
        PendingAttemptView(
            id=attempt.id,
            player_name=player.name,
            mission_title=mission.title,
            photo_url=attempt.photo_url,
            submitted_at=attempt.submitted_at,
        )
        for attempt, mission, player in rows
    ]


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


@router.post("/attempts/{attempt_id}/submit", response_model=SubmitAttemptResultView)
async def submit_attempt(
    attempt_id: uuid.UUID,
    payload: SubmitAttemptRequest,
    service: MissionService = Depends(get_mission_service),
) -> SubmitAttemptResultView:
    attempt = await _get_attempt_or_404(service, attempt_id)
    try:
        attempt, is_correct = await service.submit_attempt(
            attempt, payload.photo_url, payload.text_answer
        )
    except InvalidAttemptStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    mission = await service.mission_repo.get_mission(attempt.mission_id)
    steps = (mission.validation_config or {}).get("steps") if mission else None

    return SubmitAttemptResultView(
        **AttemptView.model_validate(attempt).model_dump(),
        is_correct=is_correct,
        total_steps=len(steps) if steps else None,
    )


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
