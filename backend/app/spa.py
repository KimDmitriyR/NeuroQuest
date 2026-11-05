"""Serve the built frontend (Vite `dist/`) from the API process.

Lets one process on one port host the whole app (no nginx, no Docker): handy for
a demo behind a tunnel. Enabled by setting FRONTEND_DIST to the dist folder.
"""

import mimetypes
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

# On Windows Python reads MIME types from the registry, where .js is sometimes
# "text/plain" - browsers then refuse to run module scripts. Pin what a Vite
# build needs.
for _ext, _type in {
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".css": "text/css",
    ".svg": "image/svg+xml",
    ".json": "application/json",
    ".webp": "image/webp",
    ".png": "image/png",
    ".woff2": "font/woff2",
}.items():
    mimetypes.add_type(_type, _ext)

_ALL_METHODS = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
_IMMUTABLE = "public, max-age=31536000, immutable"  # Vite file names carry a content hash
_NO_CACHE = "no-cache"  # always revalidate: index.html points at the current hashed files


def mount_frontend(app: FastAPI, dist_dir: str | Path) -> None:
    """Register the static files + SPA fallback. Call AFTER all API routes."""
    dist = Path(dist_dir).resolve()
    index = dist / "index.html"
    if not index.is_file():
        raise RuntimeError(
            f"FRONTEND_DIST={dist} has no index.html - run `npm run build` in frontend/ first"
        )

    # /api must never fall through to the SPA: an unknown API path (any method)
    # is a JSON 404, not an HTML page
    @app.api_route("/api/{rest:path}", methods=_ALL_METHODS, include_in_schema=False)
    async def api_not_found(rest: str) -> Response:
        raise HTTPException(status_code=404, detail="Not Found")

    @app.api_route("/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def frontend(path: str) -> FileResponse:
        if path:
            try:
                candidate = (dist / path).resolve()
                inside = candidate.is_relative_to(dist) and candidate.is_file()
            except (OSError, ValueError):
                inside = False
                candidate = index
            if inside:
                cache = _IMMUTABLE if path.startswith("assets/") else _NO_CACHE
                return FileResponse(candidate, headers={"Cache-Control": cache})
            if path.startswith("assets/"):
                # a missing hashed file must be a real 404 (not index.html
                # served as "JavaScript") so a stale tab fails loudly
                raise HTTPException(status_code=404, detail="Not Found")
        # any other path is a client-side route (/missions, /quest/123, ...)
        return FileResponse(index, headers={"Cache-Control": _NO_CACHE})
