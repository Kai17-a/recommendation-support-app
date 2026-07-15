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

bootstrap-local-users:
    uv run --directory apps/api python -m app.bootstrap.cli --department-code local-dev --department-name 'ローカル開発部' --user-name 'ローカル運用者' --email operator@example.com --oidc-subject 11111111-1111-1111-1111-111111111111 --role system_operator --status active
    uv run --directory apps/api python -m app.bootstrap.cli --department-code local-dev --department-name 'ローカル開発部' --user-name 'ローカルマネージャー' --email manager@example.com --oidc-subject 22222222-2222-2222-2222-222222222222 --role manager --status active

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
