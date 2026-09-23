import uuid


async def test_create_player(client):
    response = await client.post("/api/players", json={"name": "Тестовый игрок"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Тестовый игрок"
    assert uuid.UUID(body["id"])
    assert "created_at" in body
    assert "updated_at" in body


async def test_get_player(client):
    create_response = await client.post("/api/players", json={"name": "Игрок Два"})
    player_id = create_response.json()["id"]

    response = await client.get(f"/api/players/{player_id}")

    assert response.status_code == 200
    assert response.json()["id"] == player_id
    assert response.json()["name"] == "Игрок Два"


async def test_get_player_not_found(client):
    response = await client.get(f"/api/players/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_create_player_rejects_empty_name(client):
    response = await client.post("/api/players", json={"name": ""})

    assert response.status_code == 422
