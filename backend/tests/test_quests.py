import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.loader import load_all_cards

QR_TOKEN = "finstartup-2-0-01"


@pytest.fixture(autouse=True)
async def _seed_content(db_session: AsyncSession):
    await load_all_cards(db_session)


async def _create_player(client, name: str = "Тест") -> str:
    response = await client.post("/api/players", json={"name": name})
    return response.json()["id"]


async def _pick(client, session_id: str, label: str) -> dict:
    """Fetch the current node and submit the choice with the given label."""
    node_response = await client.get(f"/api/quests/sessions/{session_id}")
    choices = node_response.json()["current_node"]["choices"]
    choice_id = next(c["id"] for c in choices if c["label"] == label)
    response = await client.post(
        f"/api/quests/sessions/{session_id}/choices", json={"choice_id": choice_id}
    )
    return response.json()


async def test_start_quest_by_qr_token(client):
    player_id = await _create_player(client)

    response = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": QR_TOKEN}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["current_node"]["type"] == "choice"
    assert len(body["current_node"]["choices"]) == 3


async def test_start_quest_unknown_qr_token_returns_404(client):
    player_id = await _create_player(client)

    response = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": "does-not-exist"}
    )

    assert response.status_code == 404


async def test_starting_twice_resumes_the_same_session(client):
    player_id = await _create_player(client)

    first = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": QR_TOKEN}
    )
    second = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": QR_TOKEN}
    )

    assert first.json()["id"] == second.json()["id"]


async def test_full_playthrough_correct_path_grants_rewards_and_completes(client):
    player_id = await _create_player(client)
    start = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": QR_TOKEN}
    )
    session_id = start.json()["id"]

    stage1 = await _pick(client, session_id, "C")
    assert stage1["achievement_granted"]["title"] == "Финансовая самостоятельность"
    assert stage1["completed"] is False

    stage2 = await _pick(client, session_id, "C")
    assert stage2["achievement_granted"]["title"] == "Тайм-менеджмент"
    assert stage2["completed"] is False

    stage3 = await _pick(client, session_id, "C")
    assert stage3["achievement_granted"]["title"] == "Финансовая зрелость"
    assert stage3["completed"] is True
    assert stage3["next_node"] is None
    assert stage3["master_code_letter"] == {"letter": "Й", "position": 4}
    # the completion badge shares the same title as the stage-1 achievement,
    # already granted once - so it must NOT be granted a second time here
    assert stage3["completion_achievement"] is None

    final = await client.get(f"/api/quests/sessions/{session_id}")
    assert final.json()["status"] == "completed"


async def test_wrong_path_still_reaches_completion_with_final_badge(client):
    player_id = await _create_player(client)
    start = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": QR_TOKEN}
    )
    session_id = start.json()["id"]

    stage1 = await _pick(client, session_id, "A")
    assert stage1["status_label"] == "Должник"
    assert stage1["outcome"] == "negative"
    assert stage1["achievement_granted"] is None

    await _pick(client, session_id, "B")
    stage3 = await _pick(client, session_id, "B")

    assert stage3["completed"] is True
    # never got "Финансовая самостоятельность" along the way, so the
    # completion node grants it for the first time here
    assert stage3["completion_achievement"]["title"] == "Финансовая самостоятельность"
    assert stage3["master_code_letter"] == {"letter": "Й", "position": 4}


async def test_submitting_choice_from_wrong_node_is_rejected(client):
    player_id = await _create_player(client)
    start = await client.post(
        "/api/quests/start", json={"player_id": player_id, "qr_token": QR_TOKEN}
    )
    session_id = start.json()["id"]

    # a choice that belongs to stage 2, not the current stage-1 node
    stage1_node = await client.get(f"/api/quests/sessions/{session_id}")
    await _pick(client, session_id, "A")  # advance to stage 2
    stage1_choice_id = stage1_node.json()["current_node"]["choices"][0]["id"]

    response = await client.post(
        f"/api/quests/sessions/{session_id}/choices",
        json={"choice_id": stage1_choice_id},
    )

    assert response.status_code == 400


async def test_get_session_unknown_id_returns_404(client):
    response = await client.get(f"/api/quests/sessions/{uuid.uuid4()}")
    assert response.status_code == 404
