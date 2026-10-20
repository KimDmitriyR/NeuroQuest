"""Game endpoints must only be reachable by the child's own device or by the
parent who owns that child."""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.loader import load_all_cards, load_all_missions
from app.core.config import settings
from tests.helpers import create_player_on_device, issue_player_token, register_parent

QR_TOKEN = "finstartup-2-0-01"
PHOTO = "data:image/jpeg;base64,ZmFrZQ=="


@pytest.fixture(autouse=True)
async def _seed_content(db_session: AsyncSession):
    await load_all_cards(db_session)
    await load_all_missions(db_session)


async def _mission_id(client) -> str:
    missions = await client.get("/api/missions")
    return next(m["id"] for m in missions.json() if m["validation_type"] == "photo")


async def _family(client, name="Тест"):
    """Create a family; return (player_id, parent_headers, child_token) and
    leave the client WITHOUT any default credentials."""
    player_id, parent_headers, token = await create_player_on_device(client, name)
    del client.headers["X-Player-Token"]
    return player_id, parent_headers, token


def _child(token: str) -> dict:
    return {"X-Player-Token": token}


async def _start_session(client, player_id, headers) -> str:
    response = await client.post(
        "/api/quests/start",
        json={"player_id": player_id, "qr_token": QR_TOKEN},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _start_attempt(client, player_id, headers) -> str:
    response = await client.post(
        f"/api/missions/{await _mission_id(client)}/attempts",
        json={"player_id": player_id},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


# --------------------------------------------------------------- no credentials


async def test_game_endpoints_require_credentials(client):
    player_id, parent_headers, token = await _family(client)
    session_id = await _start_session(client, player_id, _child(token))
    attempt_id = await _start_attempt(client, player_id, _child(token))
    mission_id = await _mission_id(client)

    calls = [
        ("get", f"/api/players/{player_id}", None),
        ("get", f"/api/players/{player_id}/achievements", None),
        ("get", f"/api/players/{player_id}/master-code", None),
        ("post", "/api/quests/start", {"player_id": player_id, "qr_token": QR_TOKEN}),
        ("get", f"/api/quests/sessions/{session_id}", None),
        (
            "post",
            f"/api/quests/sessions/{session_id}/choices",
            {"choice_id": str(uuid.uuid4())},
        ),
        ("post", f"/api/missions/{mission_id}/attempts", {"player_id": player_id}),
        ("post", f"/api/missions/attempts/{attempt_id}/submit", {"photo_url": PHOTO}),
    ]
    for method, url, body in calls:
        response = await getattr(client, method)(url, **({"json": body} if body else {}))
        assert response.status_code == 401, (method, url, response.status_code)


async def test_unknown_ids_look_the_same_as_foreign_ones_without_credentials(client):
    # a stranger must not be able to tell "exists" from "does not exist"
    for url in (
        f"/api/quests/sessions/{uuid.uuid4()}",
        f"/api/players/{uuid.uuid4()}",
    ):
        assert (await client.get(url)).status_code == 401
    response = await client.post(
        f"/api/missions/attempts/{uuid.uuid4()}/submit", json={"photo_url": PHOTO}
    )
    assert response.status_code == 401


# --------------------------------------------------------------- the child

async def test_child_token_gives_access_to_that_child_only(client):
    player_id, _p, token = await _family(client)

    own = await client.get(f"/api/players/{player_id}", headers=_child(token))
    assert own.status_code == 200

    other_id, _op, _ot = await _family(client, "Чужой")
    foreign = await client.get(f"/api/players/{other_id}", headers=_child(token))
    assert foreign.status_code == 404


async def test_child_cannot_touch_another_childs_session_or_attempt(client):
    mine, _p, my_token = await _family(client)
    other, _op, other_token = await _family(client, "Чужой")
    session_id = await _start_session(client, other, _child(other_token))
    attempt_id = await _start_attempt(client, other, _child(other_token))
    mine_h = _child(my_token)

    assert (
        await client.get(f"/api/quests/sessions/{session_id}", headers=mine_h)
    ).status_code == 404
    assert (
        await client.post(
            f"/api/quests/sessions/{session_id}/choices",
            json={"choice_id": str(uuid.uuid4())},
            headers=mine_h,
        )
    ).status_code == 404
    assert (
        await client.post(
            "/api/quests/start",
            json={"player_id": other, "qr_token": QR_TOKEN},
            headers=mine_h,
        )
    ).status_code == 404
    assert (
        await client.post(
            f"/api/missions/{await _mission_id(client)}/attempts",
            json={"player_id": other},
            headers=mine_h,
        )
    ).status_code == 404
    assert (
        await client.post(
            f"/api/missions/attempts/{attempt_id}/submit",
            json={"photo_url": PHOTO},
            headers=mine_h,
        )
    ).status_code == 404

    # ...and the attempt really was left untouched
    pending = await client.get(
        "/api/missions/attempts/pending", headers=_p
    )  # my parent: nothing
    assert pending.json() == []


async def test_child_token_is_not_a_parent_credential(client):
    player_id, _p, token = await _family(client)
    as_bearer = {"Authorization": f"Bearer {token}"}

    assert (await client.get("/api/auth/me", headers=as_bearer)).status_code == 401
    assert (
        await client.post("/api/players", json={"name": "Хитрец"}, headers=as_bearer)
    ).status_code == 401
    assert (
        await client.get("/api/missions/attempts/pending", headers=as_bearer)
    ).status_code == 401
    assert (
        await client.get("/api/parents/me/children", headers=as_bearer)
    ).status_code == 401
    # nor can it mint more tokens, reset them, or review submissions
    assert (
        await client.post(f"/api/players/{player_id}/access-token", headers=_child(token))
    ).status_code == 401
    assert (
        await client.post(
            f"/api/players/{player_id}/access-token/reset", headers=_child(token)
        )
    ).status_code == 401
    attempt_id = await _start_attempt(client, player_id, _child(token))
    assert (
        await client.post(
            f"/api/missions/attempts/{attempt_id}/review",
            json={"approved": True},
            headers=_child(token),
        )
    ).status_code == 401


async def test_parent_token_in_player_header_is_rejected(client):
    player_id, parent_headers, _t = await _family(client)
    parent_jwt = parent_headers["Authorization"].removeprefix("Bearer ")

    response = await client.get(
        f"/api/players/{player_id}", headers={"X-Player-Token": parent_jwt}
    )
    assert response.status_code == 401


@pytest.mark.parametrize("junk", ["", "garbage", "a.b.c"])
async def test_malformed_player_token_is_401(client, junk):
    player_id, _p, _t = await _family(client)
    response = await client.get(
        f"/api/players/{player_id}", headers={"X-Player-Token": junk}
    )
    assert response.status_code == 401


async def test_player_token_signed_with_other_key_is_401(client):
    player_id, _p, _t = await _family(client)
    forged = jwt.encode(
        {
            "sub": player_id,
            "typ": "player",
            "ver": 0,
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        },
        "not-the-real-secret",
        algorithm=settings.jwt_algorithm,
    )
    response = await client.get(
        f"/api/players/{player_id}", headers={"X-Player-Token": forged}
    )
    assert response.status_code == 401


async def test_expired_player_token_is_401(client):
    player_id, _p, _t = await _family(client)
    expired = jwt.encode(
        {
            "sub": player_id,
            "typ": "player",
            "ver": 0,
            "exp": datetime.now(timezone.utc) - timedelta(seconds=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = await client.get(
        f"/api/players/{player_id}", headers={"X-Player-Token": expired}
    )
    assert response.status_code == 401


# --------------------------------------------------------------- the parent


async def test_parent_can_use_game_endpoints_for_own_child_only(client):
    player_id, parent_headers, _t = await _family(client)
    other_id, other_parent_headers, _ot = await _family(client, "Чужой")

    for url in (
        f"/api/players/{player_id}",
        f"/api/players/{player_id}/achievements",
        f"/api/players/{player_id}/master-code",
    ):
        assert (await client.get(url, headers=parent_headers)).status_code == 200

    session_id = await _start_session(client, player_id, parent_headers)
    assert (
        await client.get(f"/api/quests/sessions/{session_id}", headers=parent_headers)
    ).status_code == 200
    # a different family's parent gets nothing
    assert (
        await client.get(
            f"/api/quests/sessions/{session_id}", headers=other_parent_headers
        )
    ).status_code == 404
    assert (
        await client.get(f"/api/players/{player_id}", headers=other_parent_headers)
    ).status_code == 404
    assert (
        await client.get(f"/api/players/{other_id}", headers=parent_headers)
    ).status_code == 404


async def test_expired_parent_token_does_not_lock_out_a_valid_child_token(client):
    player_id, parent_headers, token = await _family(client)
    stale_parent = {"Authorization": "Bearer not.a.valid-token"}

    response = await client.get(
        f"/api/players/{player_id}", headers={**stale_parent, **_child(token)}
    )
    assert response.status_code == 200


async def test_legacy_parent_token_without_typ_still_works(client):
    _pid, parent_headers, _t = await _family(client)
    parent_id = (await client.get("/api/auth/me", headers=parent_headers)).json()["id"]
    legacy = jwt.encode(
        {"sub": parent_id, "exp": datetime.now(timezone.utc) + timedelta(days=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {legacy}"}
    )
    assert response.status_code == 200


# --------------------------------------------------------------- issuing/revoking


async def test_issue_token_is_parent_only_and_owner_only(client):
    player_id, parent_headers, _t = await _family(client)
    other_parent = await register_parent(client)

    anon = await client.post(f"/api/players/{player_id}/access-token")
    assert anon.status_code == 401
    stranger = await client.post(
        f"/api/players/{player_id}/access-token", headers=other_parent
    )
    assert stranger.status_code == 404
    unknown = await client.post(
        f"/api/players/{uuid.uuid4()}/access-token", headers=parent_headers
    )
    assert unknown.status_code == 404

    token = await issue_player_token(client, player_id, parent_headers)
    assert (
        await client.get(f"/api/players/{player_id}", headers=_child(token))
    ).status_code == 200


async def test_reset_revokes_old_tokens_and_returns_a_working_new_one(client):
    player_id, parent_headers, old_token = await _family(client)
    session_id = await _start_session(client, player_id, _child(old_token))

    reset = await client.post(
        f"/api/players/{player_id}/access-token/reset", headers=parent_headers
    )
    assert reset.status_code == 200
    new_token = reset.json()["access_token"]
    assert new_token != old_token

    # the leaked/old link is dead everywhere, and says so (401, not 404)
    for url in (
        f"/api/players/{player_id}",
        f"/api/players/{player_id}/master-code",
        f"/api/quests/sessions/{session_id}",
    ):
        assert (await client.get(url, headers=_child(old_token))).status_code == 401, url

    # the new one works, and so does the parent, and progress survived
    assert (
        await client.get(f"/api/quests/sessions/{session_id}", headers=_child(new_token))
    ).status_code == 200
    assert (
        await client.get(f"/api/players/{player_id}", headers=parent_headers)
    ).status_code == 200


async def test_reset_is_owner_only(client):
    player_id, _p, token = await _family(client)
    other_parent = await register_parent(client)

    assert (
        await client.post(f"/api/players/{player_id}/access-token/reset")
    ).status_code == 401
    assert (
        await client.post(
            f"/api/players/{player_id}/access-token/reset", headers=other_parent
        )
    ).status_code == 404
    # the failed attempts did not revoke anything
    assert (
        await client.get(f"/api/players/{player_id}", headers=_child(token))
    ).status_code == 200


# --------------------------------------------------------------- content stays public


async def test_mission_catalog_is_still_public(client):
    assert (await client.get("/api/missions")).status_code == 200
    mission_id = await _mission_id(client)
    assert (await client.get(f"/api/missions/{mission_id}")).status_code == 200


# --------------------------------------------------------------- GET /players/me


async def test_players_me_identifies_the_device_owner(client):
    player_id, _p, token = await _family(client, "Маша")

    response = await client.get("/api/players/me", headers=_child(token))

    assert response.status_code == 200
    assert response.json()["id"] == player_id
    assert response.json()["name"] == "Маша"


async def test_players_me_needs_a_player_token(client):
    _pid, parent_headers, _t = await _family(client)

    assert (await client.get("/api/players/me")).status_code == 401
    # a parent login alone cannot say "who is playing on this device"
    assert (
        await client.get("/api/players/me", headers=parent_headers)
    ).status_code == 401
    assert (
        await client.get("/api/players/me", headers={"X-Player-Token": "junk"})
    ).status_code == 401


async def test_players_me_rejects_a_revoked_token(client):
    player_id, parent_headers, old_token = await _family(client)
    await client.post(
        f"/api/players/{player_id}/access-token/reset", headers=parent_headers
    )

    response = await client.get("/api/players/me", headers=_child(old_token))
    assert response.status_code == 401
