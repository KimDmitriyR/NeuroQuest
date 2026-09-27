EMAIL = "parent@example.com"
PASSWORD = "supersecret123"


async def test_register_creates_parent_and_returns_token(client):
    response = await client.post(
        "/api/auth/register", json={"email": EMAIL, "password": PASSWORD}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["parent"]["email"] == EMAIL
    assert body["access_token"]
    assert body["token_type"] == "bearer"


async def test_register_duplicate_email_rejected(client):
    await client.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD})

    response = await client.post(
        "/api/auth/register", json={"email": EMAIL, "password": PASSWORD}
    )

    assert response.status_code == 409


async def test_register_rejects_short_password(client):
    response = await client.post(
        "/api/auth/register", json={"email": EMAIL, "password": "short"}
    )

    assert response.status_code == 422


async def test_login_with_correct_credentials(client):
    await client.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD})

    response = await client.post(
        "/api/auth/login", json={"email": EMAIL, "password": PASSWORD}
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_login_with_wrong_password_rejected(client):
    await client.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD})

    response = await client.post(
        "/api/auth/login", json={"email": EMAIL, "password": "wrongpassword"}
    )

    assert response.status_code == 401


async def test_login_unknown_email_rejected(client):
    response = await client.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )

    assert response.status_code == 401


async def test_me_returns_current_parent(client):
    register = await client.post(
        "/api/auth/register", json={"email": EMAIL, "password": PASSWORD}
    )
    token = register.json()["access_token"]

    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == EMAIL


async def test_me_without_token_rejected(client):
    response = await client.get("/api/auth/me")

    assert response.status_code == 401


async def test_me_with_garbage_token_rejected(client):
    response = await client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


async def test_list_children_scoped_to_own_parent(client):
    register_a = await client.post(
        "/api/auth/register", json={"email": "a@example.com", "password": PASSWORD}
    )
    headers_a = {"Authorization": f"Bearer {register_a.json()['access_token']}"}
    register_b = await client.post(
        "/api/auth/register", json={"email": "b@example.com", "password": PASSWORD}
    )
    headers_b = {"Authorization": f"Bearer {register_b.json()['access_token']}"}

    await client.post("/api/players", json={"name": "Ребёнок А"}, headers=headers_a)
    await client.post("/api/players", json={"name": "Ребёнок Б1"}, headers=headers_b)
    await client.post("/api/players", json={"name": "Ребёнок Б2"}, headers=headers_b)

    response_a = await client.get("/api/parents/me/children", headers=headers_a)
    response_b = await client.get("/api/parents/me/children", headers=headers_b)

    assert [c["name"] for c in response_a.json()] == ["Ребёнок А"]
    assert {c["name"] for c in response_b.json()} == {"Ребёнок Б1", "Ребёнок Б2"}


async def test_list_children_requires_auth(client):
    response = await client.get("/api/parents/me/children")

    assert response.status_code == 401
