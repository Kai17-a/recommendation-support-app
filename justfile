default:
    @just --list

install:
    bun install
    uv sync --directory apps/api --all-groups

api-dev:
    uv run --directory apps/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

ai-worker:
    uv run --directory apps/api dramatiq app.ai.tasks --processes 1 --threads 4

web-dev:
    bun run web:dev

infra-up:
    docker compose up -d

infra-down:
    docker compose down

db-migrate:
    uv run --directory apps/api alembic upgrade head

bootstrap-user *args:
    uv run --directory apps/api python -m app.bootstrap.cli {{args}}

lint:
    bun run web:lint
    uv run --directory apps/api ruff check .
    uv run --directory apps/api ty check

format:
    bun run web:format
    uv run --directory apps/api ruff format .

test:
    bun run web:test
    uv run --directory apps/api pytest
