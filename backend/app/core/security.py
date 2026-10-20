import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


PARENT_TOKEN_TYPE = "parent"
PLAYER_TOKEN_TYPE = "player"


@dataclass(frozen=True)
class PlayerClaims:
    player_id: uuid.UUID
    version: int


def create_access_token(parent_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(parent_id), "typ": PARENT_TOKEN_TYPE, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> uuid.UUID | None:
    """Decode a PARENT token. Player tokens are rejected here on purpose."""
    payload = _decode(token)
    if payload is None:
        return None
    # tokens issued before `typ` existed carry no such claim: they are parent tokens
    if payload.get("typ", PARENT_TOKEN_TYPE) != PARENT_TOKEN_TYPE:
        return None
    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        return None


def create_player_token(player_id: uuid.UUID, version: int) -> str:
    """Long-lived credential for a child's device, scoped to ONE player.

    `version` mirrors Player.token_version: bumping it in the DB revokes every
    token issued before (used when a link leaks).
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.player_token_expire_days)
    payload = {
        "sub": str(player_id),
        "typ": PLAYER_TOKEN_TYPE,
        "ver": version,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_player_token(token: str) -> PlayerClaims | None:
    payload = _decode(token)
    if payload is None or payload.get("typ") != PLAYER_TOKEN_TYPE:
        return None
    try:
        version = payload["ver"]
        if not isinstance(version, int) or isinstance(version, bool):
            return None
        return PlayerClaims(player_id=uuid.UUID(payload["sub"]), version=version)
    except (KeyError, ValueError):
        return None


def _decode(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.InvalidTokenError:
        return None
