from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.models.parent_account import ParentAccount
from app.repositories.parent_repository import ParentRepository
from app.schemas.player import PlayerRead

router = APIRouter(prefix="/api/parents", tags=["parents"])


@router.get("/me/children", response_model=list[PlayerRead])
async def list_my_children(
    parent: ParentAccount = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> list[PlayerRead]:
    children = await ParentRepository(db).list_children(parent.id)
    return [PlayerRead.model_validate(c) for c in children]
