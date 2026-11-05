#!/bin/sh
# Container entrypoint: refuse an unsafe configuration, migrate, seed, serve.
set -eu

DEV_SECRET="dev-insecure-secret-change-me"

if [ -z "${JWT_SECRET_KEY:-}" ]; then
  echo "FATAL: JWT_SECRET_KEY is not set. Refusing to start." >&2
  echo "       Generate one: python -c \"import secrets; print(secrets.token_urlsafe(48))\"" >&2
  exit 1
fi
if [ "$JWT_SECRET_KEY" = "$DEV_SECRET" ]; then
  echo "FATAL: JWT_SECRET_KEY is the public development default. Refusing to start." >&2
  exit 1
fi
if [ "${#JWT_SECRET_KEY}" -lt 32 ]; then
  echo "FATAL: JWT_SECRET_KEY is shorter than 32 characters. Refusing to start." >&2
  exit 1
fi

echo "Applying database migrations..."
alembic upgrade head

if [ "${SEED_CONTENT:-1}" = "1" ]; then
  echo "Loading game content (idempotent)..."
  python -m app.content.seed
fi

# Behind nginx (the only thing that can reach this port) the real client
# address comes from X-Forwarded-For, which nginx overwrites with $remote_addr.
# Rate limits depend on it.
exec uvicorn app.main:app \
  --host 0.0.0.0 --port 8000 \
  --proxy-headers --forwarded-allow-ips="${FORWARDED_ALLOW_IPS:-*}"
