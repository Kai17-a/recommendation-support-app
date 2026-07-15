# Production runbook

## Deployment

Build from `apps/api/Dockerfile`. Run Alembic as a one-shot release job before replacing API and
worker containers. `compose.production.yml` is a hardened single-host example; production TLS must
terminate at a managed load balancer or reverse proxy, with HTTP redirected to HTTPS.

Inject `DATABASE_URL`, S3 credentials, and AI provider keys from the platform secret manager. Never
commit `.env.production`. Rotate database/S3 credentials and referenced AI secrets at least every
90 days and immediately after suspected disclosure. Restrict S3 credentials to the Markdown bucket.

## Monitoring and alerts

- Probe `/health` for liveness and `/ready` for PostgreSQL, Redis, and object-storage readiness.
- Collect JSON stdout logs and index `request_id`, `status_code`, and `duration_ms`.
- Alert on readiness failure for 5 minutes, 5xx rate over 2%, p95 latency over 2 seconds, worker
  queue age over 5 minutes, failed AI jobs, PostgreSQL storage, and backup age over 26 hours.
- Logs must not include Markdown bodies, tokens, credentials, or personal-data fields.

## Backup and restore

Run `scripts/backup.sh` daily from an isolated job with PostgreSQL and MinIO clients. Encrypt the
backup destination with a managed key, retain daily copies for 35 days, and replicate off-site.
Quarterly, restore into an isolated environment using `scripts/restore.sh`, verify row/object counts,
sample retained Markdown hashes, authentication, and audit-log continuity, then destroy the drill.

## S3 and TLS

Enable bucket versioning, default SSE-KMS (or AES256 where KMS is unavailable), public-access block,
and lifecycle policy `ops/s3-lifecycle.json`. TLS 1.2+ is required on all external and service
connections. The production compose sets SSE-S3 per upload; use bucket policy to deny unencrypted
writes as defense in depth.

## Security and load verification

Before release, run dependency/image scanning, secret scanning, SAST, and authenticated DAST against
a non-production environment. Verify IDOR tests across departments and both roles. Load-test list and
detail APIs against the 2-second target, writes against 3 seconds, and Markdown uploads at the 10 MiB
boundary. Do not load-test production without an approved window and rollback owner.

## Incident response

Preserve structured logs and audit logs, revoke affected secrets, disable compromised OIDC subjects,
and isolate workers if data exfiltration is suspected. Recovery order is PostgreSQL, object storage,
Redis, migration job, API, then workers. Record timestamps and request IDs throughout the incident.
