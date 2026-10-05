import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parent_account import ParentAccount
from app.models.player import Player


class ParentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> ParentAccount | None:
        result = await self.db.execute(
            select(ParentAccount).where(ParentAccount.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, parent_id: uuid.UUID) -> ParentAccount | None:
        result = await self.db.execute(
            select(ParentAccount).where(ParentAccount.id == parent_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        password_hash: str,
        terms_accepted_at: datetime,
        terms_version: str,
    ) -> ParentAccount:
        parent = ParentAccount(
            email=email,
            password_hash=password_hash,
            terms_accepted_at=terms_accepted_at,
            terms_version=terms_version,
        )
        self.db.add(parent)
        await self.db.commit()
        await self.db.refresh(parent)
        return parent

    async def list_children(self, parent_id: uuid.UUID) -> list[Player]:
        result = await self.db.execute(
            select(Player).where(Player.parent_id == parent_id).order_by(Player.created_at)
        )
        return list(result.scalars().all())
