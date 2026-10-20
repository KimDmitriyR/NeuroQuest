import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token, decode_player_token
from app.db.session import AsyncSessionLocal
from app.models.parent_account import ParentAccount
from app.models.player import Player
from app.repositories.parent_repository import ParentRepository
from app.repositories.player_repository import PlayerRepository

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


async def get_optional_parent(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> ParentAccount | None:
    """The parent behind the Bearer token, or None.

    Lenient on purpose: an expired parent token must not lock out a child whose
    own player token is still valid. The strict variant is get_current_parent.
    """
    if credentials is None:
        return None
    parent_id = decode_access_token(credentials.credentials)
    if parent_id is None:
        return None
    return await ParentRepository(db).get_by_id(parent_id)


class PlayerAccess:
    """Decides whether the caller may act on behalf of a given child.

    A caller is allowed in if EITHER
      * they hold a valid, non-revoked player token for exactly that child
        (the child's own device, sent in the X-Player-Token header), or
      * they are logged in as the parent who owns that child.

    No valid credential at all -> 401.
    Valid credential but not for this child (or the child does not exist)
    -> 404, so ids cannot be probed.
    """

    def __init__(
        self,
        db: AsyncSession,
        parent: ParentAccount | None,
        player_token: str | None,
    ):
        self.players = PlayerRepository(db)
        self.parent = parent
        self.claims = decode_player_token(player_token) if player_token else None

    def ensure_authenticated(self) -> None:
        """401 unless the caller presented at least one valid credential.

        Call this FIRST in routes that look an object up by its own id, so that
        "does not exist" and "not yours" are indistinguishable to strangers.
        """
        if self.parent is None and self.claims is None:
            raise HTTPException(status_code=401, detail="Not authenticated")

    async def require(
        self, player_id: uuid.UUID, not_found: str = "Player not found"
    ) -> Player:
        self.ensure_authenticated()

        player = await self.players.get_by_id(player_id)
        if player is not None and self._allows(player):
            return player
        if player is not None and self._is_revoked_token_for(player):
            # the caller holds a token naming this very child, so saying
            # "revoked" reveals nothing - and tells the app to drop it
            raise HTTPException(status_code=401, detail="Access link was reset")
        raise HTTPException(status_code=404, detail=not_found)

    async def current_player(self) -> Player:
        """The child this device's own token belongs to (401 if none/revoked).

        Only the player token counts here: "who is playing on this device"
        is not a question a parent login can answer.
        """
        if self.claims is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        player = await self.players.get_by_id(self.claims.player_id)
        if player is None or player.token_version != self.claims.version:
            raise HTTPException(status_code=401, detail="Access link was reset")
        return player

    def _is_revoked_token_for(self, player: Player) -> bool:
        return (
            self.claims is not None
            and self.claims.player_id == player.id
            and self.claims.version != player.token_version
        )

    def _allows(self, player: Player) -> bool:
        if self.parent is not None and player.parent_id == self.parent.id:
            return True
        return (
            self.claims is not None
            and self.claims.player_id == player.id
            and self.claims.version == player.token_version
        )


async def get_player_access(
    parent: ParentAccount | None = Depends(get_optional_parent),
    x_player_token: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> PlayerAccess:
    return PlayerAccess(db, parent, x_player_token)
