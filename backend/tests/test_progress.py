import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.loader import load_all_cards

QR_TOKEN = "finstartup-2-0-01"


@pytest.fixture(autouse=True)
async def _seed_content(db_session: AsyncSession):
    await load_all_cards(db_session)


async def _create_player(client) -> str:
    response = await client.post("/api/players", json={"name": "Тест"})
    return response.json()["id"]


async def _complete_card_1(client, player_id: str) -> None:
    start = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": QR_TOKEN}
    )
    session_id = start.json()["id"]
    for _ in range(3):
        node = await client.get(f"/api/quests/sessions/{session_id}")
        choice_id = next(
            c["id"]
            for c in node.json()["current_node"]["choices"]
            if c["label"] == "C"
        )
        await client.post(
            f"/api/quests/sessions/{session_id}/choices", json={"choice_id": choice_id}
        )


async def test_achievements_empty_before_playing(client):
    player_id = await _create_player(client)

    response = await client.get(f"/api/players/{player_id}/achievements")

    assert response.status_code == 200
    assert response.json() == []


async def test_achievements_after_playthrough(client):
    player_id = await _create_player(client)
    await _complete_card_1(client, player_id)

    response = await client.get(f"/api/players/{player_id}/achievements")

    titles = [a["title"] for a in response.json()]
    assert titles == [
        "Финансовая самостоятельность",
        "Тайм-менеджмент",
        "Финансовая зрелость",
    ]


async def test_achievements_unknown_player_404(client):
    response = await client.get(f"/api/players/{uuid.uuid4()}/achievements")
    assert response.status_code == 404


async def test_master_code_masks_unearned_letters(client):
    player_id = await _create_player(client)

    response = await client.get(f"/api/players/{player_id}/master-code")

    body = response.json()
    assert body["unlocked_count"] == 0
    assert body["is_complete"] is False
    assert all(slot["letter"] is None for slot in body["slots"])


async def test_master_code_reveals_letter_after_playthrough(client):
    player_id = await _create_player(client)
    await _complete_card_1(client, player_id)

    response = await client.get(f"/api/players/{player_id}/master-code")

    body = response.json()
    assert body["unlocked_count"] == 1
    slot = next(s for s in body["slots"] if s["position"] == 4)
    assert slot["letter"] == "Й"
    assert slot["unlocked"] is True


async def test_master_code_unknown_player_404(client):
    response = await client.get(f"/api/players/{uuid.uuid4()}/master-code")
    assert response.status_code == 404
