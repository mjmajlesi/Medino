# Phase 6 API contract audit

Verified against the frontend and backend source on 2026-10-03. Frontend files and mock mode were not changed.

## Lesson filtering

`GET /api/lessons/` accepts `section`, `search`, `professor`, `term`, and `type` together. It returns the existing plain `Lesson[]` representation without pagination. `section` matches `Section.slug` exactly; unknown slugs return `[]`. `search` uses case-insensitive substring matching on `Lesson.title` or `Professor.name`; `professor` uses case-insensitive substring matching on `Professor.name`. The mock uses JavaScript `includes`, so English case matching is intentionally broader in the backend. SQLite Unicode case behavior is limited by SQLite. `term` must be a positive integer. `type` must be one of `note`, `video`, `sample`, or `summary`, and only lessons with an approved Resource of that type match. Duplicate resource matches produce one lesson. Empty text filters are ignored. Unknown query parameters are ignored, preserving the prior endpoint behavior; malformed `term` and `type` values return field-keyed HTTP 400 errors.

## Frontend service matrix

The response column describes the actual backend response; `yes` in the existence column refers to the route, not an implemented page. `api.ts` supplies the `/api` base URL and Bearer access token to service calls.

| Frontend function | Method and backend endpoint | Request | Backend response | Exists / compatible | Required frontend change |
| --- | --- | --- | --- | --- | --- |
| `getSections` | GET `/api/sections/` | none | plain `Section[]` | yes / yes | None for contract; wire Sections page. |
| `getLessons` | GET `/api/lessons/` | optional `section`, `search`, `professor`, `type`, `term` query parameters | plain `Lesson[]` | yes / yes | Parse route query string and display results, filters, empty/error states. |
| `getLessonDetail` | GET `/api/lessons/{id}/` | numeric string ID in route | `{lesson: Lesson, resources: Resource[]}` with approved resources only | yes / yes for real data | Use backend IDs and handle 404; align mock visibility. |
| `countByType` | no HTTP call | `Resource[]` | local type counts | not applicable | Pass approved resources if used with mocks or private lists. |
| `getStats` | GET `/api/stats/` | none | `{lessons, notes, videos, samples, summaries}` numbers | yes / yes | Handle request errors in `StatsBar` rather than showing zero as success. |
| `login` | POST `/api/auth/login/` | JSON `{student_no, password}` | `{user: StudentUser, access: string, refresh: string}` | yes / shape compatible | Implement UI and session handling; staff role is unavailable in `user`. |
| `register` | POST `/api/auth/register/` | JSON `first_name`, `last_name`, `student_no`, `entry_year`, `current_term`, `password` | same auth result, HTTP 201 | yes / shape compatible | Implement validation/error UI and session handling. |
| `logout` | no HTTP call | removes `medino_token` | no response | not applicable | Clear central auth state, refresh token, and protected query cache too. |
| `submitUpload` | POST `/api/uploads/` | multipart `lesson`, `professor`, `type`, `title`, optional `description`, `file` | `{id: string, status: 'pending' \| 'approved'}`, HTTP 201 | yes / payload compatible; return type is wrong for staff | Change result union; implement form and use selected Lesson's exact professor name. |
| `getPendingUploads` | GET `/api/admin/pending/` | Bearer staff token | plain pending `Resource[]` | yes / runtime compatible; TS return is implicit `any` | Add `Promise<Resource[]>`, staff UI and 401/403 handling. |
| `reviewUpload` | POST `/api/admin/approve/{id}/` | JSON `{action: 'approve' \| 'reject'}` | `{id: string, status: 'approved' \| 'rejected'}` | yes / runtime compatible; TS return is implicit `any` | Add return type and update/invalidate queue and public queries. |

`api.ts` is a shared Axios client, not a separate endpoint. Its interceptor adds `Authorization: Bearer <medino_token>` whenever that key exists.

### Backend endpoints with no current frontend service function

| Endpoint | Backend contract | Frontend integration needed |
| --- | --- | --- |
| POST `/api/auth/token/refresh/` | `{refresh: string}` to `{access: string, refresh?: string}`; refresh rotation depends on JWT settings | Add refresh storage/use and retry policy if persistent sessions are desired. |
| GET `/api/auth/me/` | Bearer token to `StudentUser`; anonymous 401 | Add a typed service call for session restoration and Profile. |
| GET `/api/uploads/mine/` | Bearer token to own `Resource[]`, all statuses | Add a typed service call for Profile. |
| GET `/api/resources/{id}/file/` | File stream; public if approved, otherwise only owner/staff with Bearer | Approved URLs work directly. Fetch private files as authenticated blobs for previews/downloads. |
| GET `/api/health/` | JSON health status | No UI call is currently necessary. |

## TypeScript and JSON audit

| Type or result | Finding |
| --- | --- |
| `Section` | Backend sends `id` as string, `slug`, `title`, and `description` as a string even when empty. TS makes `description` optional, which is safe but less precise. Mock IDs such as `sec-basic` differ from database numeric-string IDs. The model permits slugs beyond the six values in the TS `SectionSlug` union; current seed data stays within the union. |
| `Lesson` | Backend sends string `id`, section slug, title, professor name, numeric term, and omits blank `code`. TS matches for current seeded sections; its `section_slug` union has the same future expansion constraint. Mock IDs such as `les-anatomy` cannot be sent to the numeric detail URL. |
| `LessonDetail` | Shape matches. Backend resources are approved-only; mock detail includes the pending resource. |
| `Resource` | Backend sends string IDs, the declared type/status unions, `file_url`, `uploader_name`, and ISO datetime `created_at`; blank `description` and `duration` are omitted. TS matches. Mock dates are date-only and URLs are `#`. Private local `file_url` needs authorization. |
| `StudentUser` | Backend sends strings for `entry_year` and `current_term` (empty string when unset), matching TS. No `is_staff` field is sent, so frontend cannot reliably derive staff route access from auth results or `/me/`. |
| `AuthResult` | `MockAuthResult` has the correct `user`, `access`, `refresh` shape. It should be renamed/exported as a real result type; Axios real responses are untyped at the call site. Refresh is returned but discarded. |
| `RegisterInput` | TS uses string year/term via `StudentUser`; the backend accepts numeric strings and returns strings. UI should validate positive integers before sending. |
| Upload result | `submitUpload` currently promises only `status: 'pending'`; staff receives `'approved'`. Use exactly `'pending' \| 'approved'`. |
| Stats result | `SiteStats` keys and numeric values match exactly. |
| Moderation result | Runtime shape is `{id: string, status: 'approved' \| 'rejected'}`. Frontend has no explicit return type. |
| Pending list | Runtime is `Resource[]`; frontend has no explicit return type. |

### Auth integration gaps

- The only persisted value is the access token in `localStorage`. The returned refresh token is not stored or used. There is no `/me/` service call, session restoration, auth state/store, 401 recovery, or protected route guard.
- `/upload` and `/profile` are not guarded in the router; `/admin` and `/admin/pending` have no staff guard. The backend does enforce permissions when real requests are made.
- The backend user representation does not expose `is_staff`. A coordinated backend response addition and TS type update is recommended before building staff route guards. Do not infer staff status from a mock token or a client-side flag.
- A direct `<a href>` or `<video src>` cannot attach the Bearer header required for pending/rejected local files. Admin and owner previews must fetch with the authenticated API client as a blob and use an object URL, or use a separately designed secure delivery mechanism. Approved files can use the URL directly.
- For an external URL Resource, the backend controls whether its URL appears in public API responses but cannot enforce access at the third-party destination.
- Clear any `mock-access` token before real API testing. After moderation, invalidate pending, lesson detail, stats, and relevant owner queries.

## Mock versus backend behavior

Intentional data and security differences:

- Academic seed data mirrors the mock's six sections and 12 lessons, but database IDs are numeric strings instead of `sec-*` and `les-*`. Database resources are currently empty; the mock has sample resources. Counts and detail lists therefore differ until real resources are uploaded.
- Mock `file_url` values are `#` and `created_at` values are date-only. Backend URLs are actual HTTP URLs or external URLs, and timestamps are full ISO datetimes.
- Mock lesson detail includes a pending Resource; backend detail deliberately excludes pending/rejected Resources. Type filtering and stats in both modes consider approved resources only.
- Mock login accepts any password, registration does no server-like validation, and both can issue fake tokens. Backend validates credentials, registration fields, and password strength.
- Mock upload always returns pending and does not add a Resource to a list. Backend staff upload is immediately approved and uploads persist.
- Mock moderation does not enforce staff authorization, state transitions, or persistent queue changes. Backend enforces all three. Private file access is also enforced only by the backend.

Behavior to reconcile before mock removal:

- The mock search and professor filters use case-sensitive `includes`; backend uses `icontains`, with SQLite-dependent Unicode case behavior. Both trim text and match substrings.
- `countByType` counts whatever array it is passed. With mock detail, that could include pending resources; the real detail array cannot.
- Current `getPendingUploads`/`reviewUpload` return values have no explicit TS types. Current auth result type is named for the mock despite matching the real response.
- `StatsBar` renders zero counts on fetch errors, while `SectionCards` can render zero lesson counts if the lessons request fails. Add explicit error states during integration.

## Route and page readiness

| Page | Current state and service calls | Required access and query string | Backend ready? | Frontend work |
| --- | --- | --- | --- | --- |
| Home `/` | Implemented; `getStats`, `getSections`, `getLessons({})` | Public; QuickSearch writes `search`, SectionCards writes `section` | Yes | Handle stats/lesson request errors; later link real data. |
| Sections `/sections` | Placeholder; no calls | Public | Yes: `getSections`, `getLessons` | Build section overview and links. |
| Lessons `/lessons` | Placeholder; no calls | Public; must read/write `section`, `search`, `professor`, `term`, `type` | Yes after Phase 6 | Build list, filters, query state, loading/empty/error states. |
| Lesson detail `/lessons/:id` | Placeholder; no calls | Public; numeric-string backend ID | Yes | Fetch detail; show approved-only Resource tabs and 404. |
| Upload `/upload` | Placeholder; no calls | Authenticated; optional originating lesson ID to preselect | Yes | Form, validation, submit, status result, guard. |
| Login `/login` | Placeholder; no calls | Guest UI | Yes | Form, token handling, navigation, errors. |
| Register `/register` | Placeholder; no calls | Guest UI | Yes | Form, validation, auth state, errors. |
| Profile `/profile` | Placeholder; no calls | Authenticated | Yes: `/me/`, `/uploads/mine/` | Add services, profile and status list, private file fetch. |
| Admin dashboard `/admin` | Placeholder; no calls | Staff only | Partly: stats and pending queue; no bespoke dashboard API | Design summary from existing endpoints; guard. |
| Admin pending `/admin/pending` | Placeholder; no calls | Staff only | Yes | Queue, authenticated preview, approve/reject, query invalidation. |
| 404 `*` | Implemented; no calls | Public | Not applicable | No API work. |

No frontend hooks, auth store, or router guards exist yet. `QuickSearch` and `SectionCards` create URLs that the placeholder Lessons page does not currently read.

## Development environment and CORS

Recommended single-host local setup: frontend `http://localhost:5173`, backend `http://localhost:8000`, `VITE_API_URL=http://localhost:8000/api`, backend `ALLOWED_HOSTS=localhost,127.0.0.1`, and backend `CORS_ALLOWED_ORIGINS=http://localhost:5173`. Keep `VITE_USE_MOCK=true` until each real feature is integrated and verified. Backend settings read environment variables directly; `.env.example` alone does not load them.

The different ports make the requests cross-origin. If the browser uses `http://127.0.0.1:5173`, also allow that exact origin in `CORS_ALLOWED_ORIGINS`. Switching the frontend itself between `localhost` and `127.0.0.1` splits browser storage by origin and can confuse token testing. Keep hostnames consistent where practical. The backend URL includes `/api`; service paths supply the remainder. No frontend environment file was modified.

## Recommended Phase 7 order

1. Agree a minimal staff-role field in backend auth responses and `/me/`, then add shared TS result types.
2. Add typed `/me/`, refresh, and `/uploads/mine/` service functions and central auth state with session restoration, expiry handling, and logout cleanup.
3. Build login and registration pages, then authenticated and staff route guards.
4. Build Lessons list query-string synchronization and five filters; wire QuickSearch and SectionCards destinations.
5. Build Lesson detail tabs from approved Resources, handling real IDs and 404s.
6. Build upload form and Profile, including authenticated private file downloads/previews.
7. Build admin pending moderation and dashboard; invalidate affected query caches after actions.
8. Build Sections overview and polish Home error handling.
9. Integrate and verify each feature against the real API, reconcile mock behavior, and disable mock mode only after those checks pass.

Phase 7 is **FRONTEND REAL API INTEGRATION**. No Phase 7 implementation was done here.
