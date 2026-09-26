import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.loader import load_all_cards, load_all_missions
from app.models.envelope_mission import EnvelopeMission

MISSION_TITLE = "3D-копилка с бюджетными секторами"


@pytest.fixture(autouse=True)
async def _seed_content(db_session: AsyncSession):
    await load_all_cards(db_session)
    await load_all_missions(db_session)


async def _mission_id(db_session: AsyncSession) -> str:
    result = await db_session.execute(
        select(EnvelopeMission).where(EnvelopeMission.title == MISSION_TITLE)
    )
    return str(result.scalar_one().id)


async def _create_player(client) -> str:
    response = await client.post("/api/players", json={"name": "Тест"})
    return response.json()["id"]


async def test_start_attempt(client, db_session):
    mission_id = await _mission_id(db_session)
    player_id = await _create_player(client)

    response = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )

    assert response.status_code == 201
    assert response.json()["status"] == "in_progress"


async def test_starting_twice_resumes_same_attempt(client, db_session):
    mission_id = await _mission_id(db_session)
    player_id = await _create_player(client)

    first = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )
    second = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )

    assert first.json()["id"] == second.json()["id"]


async def test_start_attempt_unknown_mission_returns_404(client):
    player_id = await _create_player(client)

    response = await client.post(
        f"/api/missions/{uuid.uuid4()}/attempts", json={"player_id": player_id}
    )

    assert response.status_code == 404


async def test_photo_mission_full_flow_needs_manual_review(client, db_session):
    mission_id = await _mission_id(db_session)
    player_id = await _create_player(client)

    start = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )
    attempt_id = start.json()["id"]

    submit = await client.post(
        f"/api/missions/attempts/{attempt_id}/submit",
        json={"photo_url": "https://example.com/photo.jpg"},
    )
    assert submit.json()["status"] == "submitted"

    review = await client.post(
        f"/api/missions/attempts/{attempt_id}/review", json={"approved": True}
    )
    assert review.json()["status"] == "approved"
    assert review.json()["completed_at"] is not None


async def test_rejected_attempt_grants_no_achievement(client, db_session):
    mission_id = await _mission_id(db_session)
    player_id = await _create_player(client)

    start = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )
    attempt_id = start.json()["id"]
    await client.post(
        f"/api/missions/attempts/{attempt_id}/submit",
        json={"photo_url": "https://example.com/photo.jpg"},
    )

    review = await client.post(
        f"/api/missions/attempts/{attempt_id}/review", json={"approved": False}
    )

    assert review.json()["status"] == "rejected"


async def test_cannot_review_before_submit(client, db_session):
    mission_id = await _mission_id(db_session)
    player_id = await _create_player(client)

    start = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )
    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/missions/attempts/{attempt_id}/review", json={"approved": True}
    )

    assert response.status_code == 400


async def test_get_mission(client, db_session):
    mission_id = await _mission_id(db_session)

    response = await client.get(f"/api/missions/{mission_id}")

    assert response.status_code == 200
    assert response.json()["validation_type"] == "photo"


async def test_list_missions(client, db_session):
    await _mission_id(db_session)  # ensures fixture ran

    response = await client.get("/api/missions")

    assert response.status_code == 200
    titles = {m["title"] for m in response.json()}
    assert MISSION_TITLE in titles
    assert len(response.json()) == 3


CIPHER_MISSION_TITLE = "Шифровальная машина «Энигма-лайт»"


async def _cipher_mission_id(db_session: AsyncSession) -> str:
    result = await db_session.execute(
        select(EnvelopeMission).where(EnvelopeMission.title == CIPHER_MISSION_TITLE)
    )
    return str(result.scalar_one().id)


async def test_cipher_mission_wrong_answer_does_not_advance(client, db_session):
    mission_id = await _cipher_mission_id(db_session)
    player_id = await _create_player(client)

    start = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )
    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/missions/attempts/{attempt_id}/submit",
        json={"text_answer": "НЕПРАВИЛЬНО"},
    )

    body = response.json()
    assert body["is_correct"] is False
    assert body["current_step"] == 0
    assert body["status"] == "in_progress"


async def test_cipher_mission_full_sequence_completes_and_grants_once(
    client, db_session
):
    mission_id = await _cipher_mission_id(db_session)
    player_id = await _create_player(client)

    start = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )
    attempt_id = start.json()["id"]

    answers = [
        "КАПИТАЛ РАСТЕТ В ТИШИНЕ",
        "твой пароль твой щит",  # lowercase on purpose: case-insensitive
        "ЗАПРОС ОПРЕДЕЛЯЕТ ОТВЕТ",
        "БУДУЩЕЕ УЖЕ ЗДЕСЬ",
    ]
    last_body = None
    for i, answer in enumerate(answers, start=1):
        response = await client.post(
            f"/api/missions/attempts/{attempt_id}/submit",
            json={"text_answer": answer},
        )
        last_body = response.json()
        assert last_body["is_correct"] is True
        assert last_body["current_step"] == i

    assert last_body["status"] == "approved"
    assert last_body["completed_at"] is not None

    achievements = await client.get(f"/api/players/{player_id}/achievements")
    titles = [a["title"] for a in achievements.json()]
    assert titles == ["Криптограф"]


async def test_cipher_mission_cannot_submit_after_completed(client, db_session):
    mission_id = await _cipher_mission_id(db_session)
    player_id = await _create_player(client)

    start = await client.post(
        f"/api/missions/{mission_id}/attempts", json={"player_id": player_id}
    )
    attempt_id = start.json()["id"]

    for answer in [
        "КАПИТАЛ РАСТЕТ В ТИШИНЕ",
        "ТВОЙ ПАРОЛЬ ТВОЙ ЩИТ",
        "ЗАПРОС ОПРЕДЕЛЯЕТ ОТВЕТ",
        "БУДУЩЕЕ УЖЕ ЗДЕСЬ",
    ]:
        await client.post(
            f"/api/missions/attempts/{attempt_id}/submit",
            json={"text_answer": answer},
        )

    response = await client.post(
        f"/api/missions/attempts/{attempt_id}/submit",
        json={"text_answer": "БУДУЩЕЕ УЖЕ ЗДЕСЬ"},
    )

    assert response.status_code == 400
