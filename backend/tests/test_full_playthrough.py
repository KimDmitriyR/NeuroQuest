import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.loader import load_all_cards

ALL_QR_TOKENS = [
    "finstartup-2-0-01",
    "finstartup-2-0-02",
    "finstartup-2-0-03",
    "finstartup-2-0-04",
    "kibershchit-01",
    "kibershchit-02",
    "kibershchit-03",
    "kibershchit-04",
    "ai-logika-01",
    "ai-logika-02",
    "ai-logika-03",
    "ai-logika-04",
]


@pytest.fixture(autouse=True)
async def _seed_content(db_session: AsyncSession):
    await load_all_cards(db_session)


async def _create_player(client) -> str:
    import uuid as _uuid

    email = f"parent-{_uuid.uuid4()}@example.com"
    reg = await client.post(
        "/api/auth/register", json={"email": email, "password": "supersecret123", "accept_terms": True}
    )
    token = reg.json()["access_token"]
    response = await client.post(
        "/api/players",
        json={"name": "Финалист"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


async def _play_card_choosing_first_option(client, player_id: str, qr_token: str) -> None:
    """Walks a single card to completion, always picking choice 'A' at every
    stage - deliberately the 'wrong'/first option, to prove every card's
    graph reaches its completion node and grants its reward regardless of
    path, not just the curated 'correct' path already covered elsewhere."""
    start = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": qr_token}
    )
    assert start.status_code == 201, f"{qr_token}: failed to start ({start.text})"
    session_id = start.json()["id"]

    for _ in range(20):  # safety cap against any accidental infinite loop
        node = await client.get(f"/api/quests/sessions/{session_id}")
        assert node.status_code == 200
        choices = node.json()["current_node"]["choices"]
        assert choices, f"{qr_token}: node has no choices but isn't completion"
        choice_id = choices[0]["id"]

        result = await client.post(
            f"/api/quests/sessions/{session_id}/choices", json={"choice_id": choice_id}
        )
        assert result.status_code == 200, f"{qr_token}: choice submit failed"
        if result.json()["completed"]:
            return

    raise AssertionError(f"{qr_token}: did not reach completion within 20 stages")


async def test_full_game_all_12_cards_assemble_the_master_code(client):
    player_id = await _create_player(client)

    for qr_token in ALL_QR_TOKENS:
        await _play_card_choosing_first_option(client, player_id, qr_token)

    master_code = await client.get(f"/api/players/{player_id}/master-code")
    body = master_code.json()

    assert body["is_complete"] is True
    assert body["unlocked_count"] == 12
    assert body["total_positions"] == 12

    phrase = "".join(slot["letter"] for slot in sorted(body["slots"], key=lambda s: s["position"]))
    assert phrase == "ТВОЙНОВЫЙКОД"

    achievements = await client.get(f"/api/players/{player_id}/achievements")
    # every card grants at least a completion badge, so with 12 cards there
    # should be a healthy number of distinct achievements - a low count
    # would indicate reward wiring silently failing for some cards
    assert len(achievements.json()) >= 12
