# Project Health Checklist

- [x] FastAPI app bootstraps a versioned `/api/v1` router with modular route files per domain.
- [x] SQLModel models share a timestamp mixin and soft-delete flags across core entities (users, units, payments, projects, companies, documents).
- [x] RBAC primitives are defined (Role enum + `get_current_user` dependency) and applied on route decorators for admin/agent/client scoping.
- [x] Unit/payment services include payment-plan scheduling, recalculation, warranty/payment summaries, and graph data helpers.
- [x] Document and media storage flows exist with MediaFile + DocumentTemplate/SignedDocument models and Cloudflare R2 upload/download helpers.
- [x] Notification stack persists user notifications, supports Expo push tokens, and provides admin dashboard aggregates.
- [x] Operational scaffolding is present: Alembic config, Makefile commands for migrations/run/seed/test, and a setup-focused README.
- [x] Pytest scaffolding initializes in-memory SQLModel metadata for service-layer tests.
