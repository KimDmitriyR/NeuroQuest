import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_player_token,
    decode_access_token,
    decode_player_token,
)


def test_player_token_round_trip():
    player_id = uuid.uuid4()
    claims = decode_player_token(create_player_token(player_id, 3))

    assert claims is not None
    assert claims.player_id == player_id
    assert claims.version == 3


def test_token_types_are_not_interchangeable_even_for_the_same_uuid():
    # same id on purpose: only the `typ` claim can tell them apart
    same_id = uuid.uuid4()

    assert decode_access_token(create_player_token(same_id, 0)) is None
    assert decode_player_token(create_access_token(same_id)) is None


def test_player_token_without_version_is_rejected():
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "typ": "player",
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    assert decode_player_token(token) is None


def test_player_token_with_non_integer_version_is_rejected():
    for bad in ("0", True, 1.5, None):
        token = jwt.encode(
            {
                "sub": str(uuid.uuid4()),
                "typ": "player",
                "ver": bad,
                "exp": datetime.now(timezone.utc) + timedelta(days=1),
            },
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        assert decode_player_token(token) is None, bad
