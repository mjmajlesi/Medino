# Medino API reference

This describes the current Django routes in `backend/config/urls.py` and the three backend apps. Paths have the `/api/` prefix unless stated otherwise. Send an access token as `Authorization: Bearer <access-token>` where required. Anonymous requests to protected endpoints return 401; authenticated non-staff users receive 403 on staff-only endpoints. Public section and lesson reads accept requests without a token. IDs in serialized API data are strings even though detail paths use numeric IDs. Dates in API responses use ISO 8601.

The current React application has `/admin`, `/admin/pending`, and `/admin/lessons`. The **user-management API exists, but no React `/admin/users` page or route exists**. Django Admin is `/django-admin/` and is separate from the React `/admin` route.

## Authentication

| Method and path | Access | Request | Success | Important errors |
| --- | --- | --- | --- | --- |
| `POST /api/auth/register/` | Public | JSON `first_name`, `last_name`, `student_no`, `entry_year`, `current_term`, `password` | 201 `{user, access, refresh}` | 400 for invalid, missing or duplicate fields or weak password. |
| `POST /api/auth/login/` | Public | JSON `{student_no, password}` | 200 `{user, access, refresh}` | 400 for invalid credentials or inactive account. |
| `POST /api/auth/token/refresh/` | Refresh token | JSON `{refresh}` | 200 `{access}` with current default SimpleJWT configuration | 401 for invalid/expired refresh token. |
| `GET /api/auth/me/` | Access token | None | 200 current `user` | 401 without valid access token. |

`student_no` is the login identity. The auth `user` object contains string `first_name`, `last_name`, and `student_no`; `entry_year` and `current_term` are JSON integers or `null` when unset. It also contains Boolean `is_staff` and `is_superuser`, but no user ID. Register always creates an active non-staff, non-superuser user on the server; client-supplied role fields cannot grant privileges. SimpleJWT uses its unmodified default lifetime: access 5 minutes and refresh 1 day. The backend does not expose a profile-update endpoint.

## Academics

| Method and path | Access | Request | Success | Important errors |
| --- | --- | --- | --- | --- |
| `GET /api/sections/` | Public | None | 200 plain `Section[]` | — |
| `GET /api/lessons/` | Public | Optional filters below | 200 plain `Lesson[]`, no pagination | 400 for invalid `term`, `type`, or `ordering`. |
| `GET /api/lessons/{id}/` | Public | Numeric lesson ID | 200 `{lesson: Lesson, resources: Resource[]}` with approved resources only | 404 if absent. |
| `POST /api/lessons/` | Staff | JSON lesson write fields below | 201 `Lesson` | 400 for validation, unknown section or ambiguous professor; 401/403 for auth. |
| `PUT /api/lessons/{id}/` | Staff | Complete JSON lesson write fields | 200 `Lesson` | 400 for validation; 404 if absent; 401/403 for auth. |
| `DELETE /api/lessons/{id}/` | Staff | None | 204, no body | 404 if absent; 401/403 for auth. |

`Section` contains `id`, `slug`, `title`, `description`. `Lesson` contains `id`, `section_slug`, `title`, `professor` (name), numeric `term`, `views`, ISO `created_at`, and `code` only when nonblank. Lesson detail GET is read-only: it **does not increment** `views`.

Lesson list filters can be combined:

| Query parameter | Behavior |
| --- | --- |
| `section` | Exact Section slug; an unknown slug gives an empty list. |
| `search` | Case-insensitive substring in lesson title or professor name. |
| `professor` | Case-insensitive substring in professor name. |
| `term` | Positive integer equality. |
| `type` | One of `note`, `video`, `sample`, `summary`; requires an approved Resource of that type. Duplicate matches yield one lesson. |
| `ordering` | Only `-created_at` or `-views`, with descending ID as a tie-breaker. Without it, model order is section order then ID. |

The staff lesson write fields are `section_slug`, `title`, `professor`, `term`, and optional `code`. `section_slug` must identify an existing Section. The title and professor name are trimmed; the professor name is reused if exactly one row matches, or a new Professor is created. Ambiguous existing names return 400. `term` must be positive. `PUT` replaces editable fields and clears `code` when omitted. Deleting a lesson cascades to its Resource database rows. Stored-file cleanup is scheduled after transaction commit through Django storage; a file still referenced by another Resource is retained. An unexpected storage failure is logged and can leave an orphaned file even though the database deletion succeeds. See [operations](operations.md#lesson-deletion-and-file-cleanup).

## Resources and moderation

| Method and path | Access | Request | Success | Important errors |
| --- | --- | --- | --- | --- |
| `POST /api/uploads/` | Authenticated | Multipart/form `lesson`, `type`, `title`, exactly one of `file` or `external_url`; optional `professor`, `description`, `direct` | 201 `{id: string, status: "pending"|"approved"}` | 400 for invalid source, file or professor; 403 if non-staff sends `direct=true`. |
| `GET /api/uploads/mine/` | Authenticated | None | 200 plain `Resource[]` for the current user, all statuses, newest first | 401 without token. |
| `GET /api/admin/pending/` | Staff | None | 200 plain pending `Resource[]`, newest first | 401/403 for auth. |
| `POST /api/admin/approve/{id}/` | Staff | JSON `{action: "approve"|"reject"}` | 200 `{id: string, status: "approved"|"rejected"}` | 400 for invalid action or already reviewed Resource; 404 if absent; 401/403 for auth. |
| `GET /api/resources/{id}/file/` | Public for approved stored file; otherwise owner or staff | Numeric Resource ID; Bearer token for a private file | 200 streamed file | 404 for missing/external-only file and for unauthorized private access. |

Resource types are `note`, `video`, `sample`, `summary`; states are `pending`, `approved`, `rejected`. A `Resource` response contains string `id` and `lesson_id`, `type`, `title`, `file_url`, `status`, `uploader_name`, ISO `created_at`, and nonblank `description`/`duration` when present. For a stored file, `file_url` points to the Django file endpoint; for an `external_url`, it is that external URL. Medino cannot enforce access at a third-party destination after disclosing its URL.

Uploads default to `pending`, including staff uploads. Only explicit `direct=true` from a staff user makes an upload immediately `approved` and records its review. An optional `professor` must match the selected lesson's professor name after trimming. The source must be exactly one of a file or an HTTP(S) `external_url`. The default `MAX_UPLOAD_SIZE` is 52,428,800 bytes (50 MiB); the Compose frontend Nginx also limits the entire request body to 55 MiB. File validation accepts `.pdf` or `.docx` for `note`, `sample`, and `summary`, and `.mp4` or `.webm` for `video`. It checks MIME type (or `application/octet-stream`) and file signatures/structure; `.docx` must contain the expected Word ZIP entries. File rules do not apply to an external URL.

Approved resources appear in public lesson detail and stats; pending/rejected resources are not exposed in public lesson detail. Owners see their own uploads through `/api/uploads/mine/`, and staff see the pending queue. For stored private files, Django verifies the owner or staff token and returns 404 for unauthorized requests. Nginx deliberately returns 404 for `/media/` instead of exposing `MEDIA_ROOT`.

## User management

Both active staff users and superusers with `is_staff=True` may use these endpoints. Ordinary authenticated users receive 403, anonymous callers 401. This feature changes **only** `is_staff`; `is_superuser` remains under trusted Django administrative control.

| Method and path | Access | Request | Success | Important errors |
| --- | --- | --- | --- | --- |
| `GET /api/admin/users/` | Staff | Optional `search`, `role`, `page` | 200 `{count, next, previous, results}`; 20 users per page | 400 for invalid `role` or page; 401/403 for auth. |
| `PATCH /api/admin/users/{id}/access/` | Staff | JSON `{ "is_staff": true }` or `{ "is_staff": false }` | 200 updated safe user object | 400 for missing/invalid `is_staff` or any extra field; 403 for superuser target or self-demotion; 404 if absent. |

`search` matches `student_no`, `first_name`, or `last_name` case-insensitively. `role=all` is the default; `student` means `is_staff=False`, `staff` means `is_staff=True` and `is_superuser=False`, and `superuser` means `is_superuser=True`. The result object contains string `id` and `student_no`, names, numeric-or-null `entry_year` and `current_term`, and Boolean `is_active`, `is_staff`, `is_superuser`. Passwords, hashes, JWTs, groups, and raw permissions are excluded.

A staff admin may grant staff access to a student or revoke it from **another** non-superuser staff admin. No caller, including a superuser, may modify a superuser through this endpoint or revoke their own staff access. Payloads containing `is_superuser`, `password`, `is_active`, `groups`, or any other field besides `is_staff` are rejected rather than ignored. Registration cannot create a staff user or superuser.

## Health and stats

| Method and path | Access | Success |
| --- | --- | --- |
| `GET /api/health/` | Public | 200 `{ "status": "ok" }`. |
| `GET /api/stats/` | Public | 200 `{lessons, notes, videos, samples, summaries}` with total lesson count and approved Resource counts by type. |

The frontend container also exposes `GET /healthz` with a plain `ok` response for its health check. Django Admin is at `/django-admin/`; its HTML/session/CSRF flow is distinct from the JWT API.
