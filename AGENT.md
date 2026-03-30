# AGENT.md

This file gives coding agents the minimum repo context needed to make safe, useful changes in `cortts_backend`.

## Project Summary

- Backend API for Cortts Real Estate.
- Stack: FastAPI, SQLModel, Alembic, PostgreSQL, Pydantic Settings, Pytest.
- Main domains: auth, users, companies, projects, units, payments, documents/uploads, notifications, dashboard.

## Entry Points

- App bootstrap: `app/main.py`
- API router assembly: `app/api/__init__.py`
- Config/settings: `app/core/config.py`
- DB session/engine: `app/db/session.py`
- Migrations: `alembic/`
- Tests: `tests/services/`

## Directory Guide

- `app/api/routes/`: HTTP route handlers by domain.
- `app/services/`: business logic. Prefer changes here over putting logic in routes.
- `app/models/`: SQLModel persistence models.
- `app/schemas/`: request/response schemas.
- `app/auth/`: auth dependencies and access control helpers.
- `app/core/`: config and security primitives.
- `app/seed/`: seed scripts for admin, documents, unit-agent links, and bulk seed flows.
- `app/utility/`: shared helper utilities.
- `doc/`: prompt/reference docs for AI and Figma-related flows.

## Local Commands

- Create venv: `python3 -m venv venv && source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Run API: `make run`
- Start local mail sink: `make mail-dev-up`
- Stop local mail sink: `make mail-dev-down`
- Run migrations: `make upgrade`
- Create migration: `make migrate`
- Show migration state: `make show`
- Run tests once: `make test-once`
- Watch tests: `make test`
- Seed data: `make seed-all`

## Environment Notes

Settings are loaded from `.env` via `app/core/config.py`.

Important variables used in code:

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `EMAIL_ENABLED`
- `EMAIL_BACKEND`
- `EMAIL_FROM_EMAIL`
- `EMAIL_FROM_NAME`
- `EMAIL_EXPOSE_VERIFICATION_CODE`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`
- `R2_ENDPOINT_URL`
- `R2_ACCESS_TOKEN`
- `R2_PUBLIC_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `ALLOWED_ORIGINS`

## Repo-Specific Pitfalls

- `app/db/session.py` raises immediately if `DATABASE_URL` is missing. Any change that imports that module during startup or tests can fail without env setup.
- Local email now uses Mailpit over SMTP on `localhost:1025`; the web inbox is `http://localhost:8025`.
- Service tests use isolated in-memory SQLite engines instead of the app's configured PostgreSQL engine. Follow that pattern for unit/service tests.
- `make test` uses `ptw`; `make test-once` is better for non-interactive verification.
- The repo already has uncommitted changes outside this file. Do not overwrite unrelated work.

## Change Guidelines

- Keep route files thin. Put validation-heavy or transactional logic in `app/services/`.
- When adding fields, update model, schema, service, route, and if needed Alembic migration together.
- Preserve soft-delete behavior and audit-style fields on core entities.
- Keep auth and role checks explicit in route dependencies.
- Prefer targeted tests in `tests/services/` for service changes.

## Verification Expectations

For most backend edits:

1. Run focused `pytest` coverage for the touched service/module when possible.
2. Run `make test-once` if the change is broad enough.
3. If DB schema changed, verify Alembic migration generation and upgrade path.

## Useful Existing Docs

- Project overview: `readme.md`
- Health checklist: `CHECKLIST.md`
- AI/Figma prompts: `doc/figma_agent_prompt.md`, `doc/figma_client_prompt.md`, `doc/figma_admin_prompt.md`
