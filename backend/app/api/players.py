import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.player_repository import PlayerRepository
from app.schemas.player import PlayerCreate, PlayerRead
from app.services.player_service import PlayerNotFoundError, PlayerService

router = APIRouter(prefix="/api/players", tags=["players"])


def get_player_service(db: AsyncSession = Depends(get_db)) -> PlayerService:
    return PlayerService(PlayerRepository(db))


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
