#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose=(docker compose --project-name recommendation-support-integration \
  --file "$root_dir/docker-compose.yml" \
  --file "$root_dir/docker-compose.integration.yml" \
  --profile integration)

cleanup() {
  "${compose[@]}" down --volumes --remove-orphans
}
trap cleanup EXIT

cleanup
"${compose[@]}" up --build --abort-on-container-exit \
  --exit-code-from integration-tests integration-tests
