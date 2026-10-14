# Phase 6 API contract audit (historical)

This file records the purpose and outcome of the 2026-10-03 Phase 6 audit. Its original implementation checklist described the repository **before** later authentication, frontend integration, Docker and seed work. That checklist is no longer an operational guide. For the current contract use [API reference](api.md), for running the stack use [deployment](deployment.md), and for data maintenance use [operations](operations.md).

## Lasting Phase 6 decisions

- `GET /api/lessons/` supports combinable `section`, `search`, `professor`, `term`, and approved-Resource `type` filters. It returns a plain lesson array; sorting now also accepts `ordering=-created_at` and `ordering=-views`.
- Public lesson detail includes approved Resources only. Pending and rejected uploads are not part of the public detail response. A detail GET does not increment stored `Lesson.views`.
- API Resource and Lesson IDs are serialized as strings. Stored-file URLs point to Django's authorization-aware endpoint, while external URLs point to third-party hosts that Medino cannot protect after disclosure.
- Private files require the owner or staff token. Nginx must not expose `MEDIA_ROOT` directly.

## Current state compared with that audit

- Runtime and tests require PostgreSQL; the old SQLite behavior discussion is obsolete. The catalog is now six Sections and a 75-Lesson reference dataset with 26 Professor names, not the earlier 12-Lesson seed.
- The backend auth response and `/api/auth/me/` now include both `is_staff` and `is_superuser`. The frontend has an auth store, route guards, token refresh, profile, upload, lesson list/detail, and staff moderation/lesson pages. The earlier placeholder-page and missing-auth checklist is complete or superseded.
- Mock branches remain in frontend services for local demonstration. The Compose frontend image is built with `VITE_USE_MOCK=false` and `VITE_API_URL=/api` for the real same-origin API. Avoid treating mock data or tokens as backend records.
- The backend has staff-access User Management endpoints. The current React router does **not** contain a User Management page or `/admin/users` route; frontend User Management was deliberately rolled back. Do not infer a UI from the API's existence.
- The backend's safe `AdminUser` response includes `is_superuser`, but the current frontend `StudentUser` TypeScript type still models only optional `is_staff`. This does not change the backend response; use [API reference](api.md#authentication) as the server contract.

Retain this document as an audit history marker. The linked current references supersede its original task recommendations and environment assumptions.
