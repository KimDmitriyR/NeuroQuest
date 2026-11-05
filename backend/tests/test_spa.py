import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.spa import mount_frontend


@pytest.fixture
def dist(tmp_path):
    root = tmp_path / "dist"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text("<!doctype html><title>NQ</title>")
    (root / "assets" / "app-abc123.js").write_text("console.log(1)")
    (root / "assets" / "app-abc123.css").write_text("body{}")
    (root / "favicon.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    (tmp_path / "secret.txt").write_text("TOP SECRET")  # outside dist
    return root


@pytest.fixture
async def spa_client(dist):
    app = FastAPI()

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    mount_frontend(app, dist)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_root_and_client_routes_get_index_html(spa_client):
    for path in ["/", "/missions", "/quest/123", "/parent", "/some/deep/route"]:
        r = await spa_client.get(path)
        assert r.status_code == 200, path
        assert "<title>NQ</title>" in r.text
        assert r.headers["cache-control"] == "no-cache"


async def test_real_api_routes_are_not_intercepted(spa_client):
    r = await spa_client.get("/api/health")
    assert r.json() == {"status": "ok"}


async def test_unknown_api_paths_are_json_404_for_every_method(spa_client):
    for method in ["GET", "POST", "PUT", "DELETE"]:
        r = await spa_client.request(method, "/api/nope")
        assert r.status_code == 404, method
        assert r.json() == {"detail": "Not Found"}
        assert "NQ" not in r.text


async def test_assets_are_served_with_right_mime_and_long_cache(spa_client):
    js = await spa_client.get("/assets/app-abc123.js")
    assert js.status_code == 200
    assert js.headers["content-type"].startswith("text/javascript")
    assert "immutable" in js.headers["cache-control"]
    css = await spa_client.get("/assets/app-abc123.css")
    assert css.headers["content-type"].startswith("text/css")
    svg = await spa_client.get("/favicon.svg")
    assert svg.headers["content-type"].startswith("image/svg+xml")
    assert svg.headers["cache-control"] == "no-cache"


async def test_missing_asset_is_404_not_index_html(spa_client):
    r = await spa_client.get("/assets/gone-999.js")
    assert r.status_code == 404
    assert "NQ" not in r.text


@pytest.mark.parametrize(
    "path",
    ["/../secret.txt", "/%2e%2e/secret.txt", "/assets/../../secret.txt", "/..%2fsecret.txt", "/%2e%2e%2fsecret.txt"],
)
async def test_path_traversal_never_leaks_files_outside_dist(spa_client, path):
    r = await spa_client.get(path)
    assert "TOP SECRET" not in r.text


async def test_head_request_works(spa_client):
    assert (await spa_client.head("/missions")).status_code == 200


def test_missing_index_html_fails_loudly(tmp_path):
    with pytest.raises(RuntimeError, match="npm run build"):
        mount_frontend(FastAPI(), tmp_path)
