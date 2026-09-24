import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.player_repository import PlayerRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.player import PlayerCreate, PlayerRead
from app.schemas.progress import (
    EarnedAchievementView,
    MasterCodeProgressView,
    MasterCodeSlotView,
)
from app.services.player_service import PlayerNotFoundError, PlayerService
from app.services.progress_service import ProgressService
from app.services.progress_service import PlayerNotFoundError as ProgressPlayerNotFoundError

router = APIRouter(prefix="/api/players", tags=["players"])


def get_player_service(db: AsyncSession = Depends(get_db)) -> PlayerService:
    return PlayerService(PlayerRepository(db))


def get_progress_service(db: AsyncSession = Depends(get_db)) -> ProgressService:
    return ProgressService(PlayerRepository(db), ProgressRepository(db))


@router.post("", response_model=PlayerRead, status_code=201)
async def create_player(
    payload: PlayerCreate,
    service: PlayerService = Depends(get_player_service),
) -> PlayerRead:
    player = await service.create_player(name=payload.name)
    return PlayerRead.model_validate(player)


@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(
    player_id: uuid.UUID,
    service: PlayerService = Depends(get_player_service),
) -> PlayerRead:
    try:
        player = await service.get_player(player_id)
    except PlayerNotFoundError:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerRead.model_validate(player)


@router.get("/{player_id}/achievements", response_model=list[EarnedAchievementView])
async def get_player_achievements(
    player_id: uuid.UUID,
    service: ProgressService = Depends(get_progress_service),
) -> list[EarnedAchievementView]:
    try:
        earned = await service.get_achievements(player_id)
    except ProgressPlayerNotFoundError:
        raise HTTPException(status_code=404, detail="Player not found")
    return [
        EarnedAchievementView(
            title=item.achievement.title,
            description=item.achievement.description,
            is_badge=item.achievement.is_badge,
            earned_at=item.earned_at,
        )
        for item in earned
    ]


@router.get("/{player_id}/master-code", response_model=MasterCodeProgressView)
async def get_player_master_code(
    player_id: uuid.UUID,
    service: ProgressService = Depends(get_progress_service),
) -> MasterCodeProgressView:
    try:
        progress = await service.get_master_code(player_id)
    except ProgressPlayerNotFoundError:
        raise HTTPException(status_code=404, detail="Player not found")
    return MasterCodeProgressView(
        slots=[
            MasterCodeSlotView(
                position=slot.position, letter=slot.letter, unlocked=slot.unlocked
            )
            for slot in progress.slots
        ],
        total_positions=progress.total_positions,
        unlocked_count=progress.unlocked_count,
        is_complete=progress.is_complete,
    )
