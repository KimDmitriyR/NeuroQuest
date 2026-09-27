from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.models.parent_account import ParentAccount
from app.repositories.parent_repository import ParentRepository

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_parent(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> ParentAccount:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    parent_id = decode_access_token(credentials.credentials)
    if parent_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    parent = await ParentRepository(db).get_by_id(parent_id)
    if parent is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return parent
