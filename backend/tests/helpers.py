import uuid


async def register_parent(client) -> dict:
    """Registers a fresh parent and returns their Authorization headers."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": f"parent-{uuid.uuid4()}@example.com",
            "password": "supersecret123",
            "accept_terms": True,
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def issue_player_token(client, player_id: str, parent_headers: dict) -> str:
    response = await client.post(
        f"/api/players/{player_id}/access-token", headers=parent_headers
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def create_player_on_device(
    client, name: str = "Тест"
) -> tuple[str, dict, str]:
    """A new family: parent + child, and `client` becomes the CHILD'S DEVICE.

    The httpx client then sends the child's token (X-Player-Token) on every
    request, like the real app does after the parent hands out the link -
    but NO parent token, so tests exercise the child-only code path.

    Returns (player_id, parent_headers, player_token).
    """
    parent_headers = await register_parent(client)
    created = await client.post(
        "/api/players", json={"name": name}, headers=parent_headers
    )
    player_id = created.json()["id"]
    token = await issue_player_token(client, player_id, parent_headers)
    client.headers["X-Player-Token"] = token
    return player_id, parent_headers, token
