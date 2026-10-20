import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PlayerAccess, get_current_parent, get_db, get_player_access
from app.models.parent_account import ParentAccount
from app.repositories.player_repository import PlayerRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.player import PlayerCreate, PlayerRead, PlayerTokenResponse
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
    parent: ParentAccount = Depends(get_current_parent),
    service: PlayerService = Depends(get_player_service),
) -> PlayerRead:
    player = await service.create_player(name=payload.name, parent_id=parent.id)
    return PlayerRead.model_validate(player)


@router.get("/me", response_model=PlayerRead)
async def get_my_player(
    access: PlayerAccess = Depends(get_player_access),
) -> PlayerRead:
    """Who is playing on this device? Answered from the player token alone."""
    return PlayerRead.model_validate(await access.current_player())


@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(
    player_id: uuid.UUID,
    access: PlayerAccess = Depends(get_player_access),
) -> PlayerRead:
    player = await access.require(player_id)
    return PlayerRead.model_validate(player)


async def _get_owned_player(
    player_id: uuid.UUID, parent: ParentAccount, service: PlayerService
):
    """Parent-only: the child must belong to this parent (404 otherwise)."""
    try:
        player = await service.get_player(player_id)
    except PlayerNotFoundError:
        raise HTTPException(status_code=404, detail="Player not found")
    if player.parent_id != parent.id:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("/{player_id}/access-token", response_model=PlayerTokenResponse)
async def issue_player_token(
    player_id: uuid.UUID,
    parent: ParentAccount = Depends(get_current_parent),
    service: PlayerService = Depends(get_player_service),
) -> PlayerTokenResponse:
    """Token for the child's device. Parent-only; embedded in the child link."""
    player = await _get_owned_player(player_id, parent, service)
    return PlayerTokenResponse(access_token=service.issue_token(player))


@router.post("/{player_id}/access-token/reset", response_model=PlayerTokenResponse)
async def reset_player_token(
    player_id: uuid.UUID,
    parent: ParentAccount = Depends(get_current_parent),
    service: PlayerService = Depends(get_player_service),
) -> PlayerTokenResponse:
    """Revoke every link/device handed out for this child and issue a new token."""
    player = await _get_owned_player(player_id, parent, service)
    return PlayerTokenResponse(access_token=await service.reset_token(player))


@router.get("/{player_id}/achievements", response_model=list[EarnedAchievementView])
async def get_player_achievements(
    player_id: uuid.UUID,
    access: PlayerAccess = Depends(get_player_access),
    service: ProgressService = Depends(get_progress_service),
) -> list[EarnedAchievementView]:
    await access.require(player_id)
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
    access: PlayerAccess = Depends(get_player_access),
    service: ProgressService = Depends(get_progress_service),
) -> MasterCodeProgressView:
    await access.require(player_id)
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
