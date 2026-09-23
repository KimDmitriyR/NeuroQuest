async def test_health_check(client):
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_database_health_check(client):
    response = await client.get("/api/health/db")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == 1
