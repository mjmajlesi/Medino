# Medino operations

Run Docker commands from the repository root with the ignored `.env.docker` file prepared as in [deployment](deployment.md). Run host Python commands from `backend/` with `backend/.env` configured for PostgreSQL. Endpoint details are in [API reference](api.md).

## Academic seed and prune

The reference catalog is [lessons-seed.json](lessons-seed.json): 75 unique `(section_slug, title)` lesson identities and 26 professor names. `seed_academics.py` embeds the corresponding lesson tuples and six Section definitions; **it does not read the JSON file at runtime**. One of the six Sections (`stage`) currently has no catalog lessons. Keep both representations aligned when changing the catalog. On an empty database, normal seed produces six Sections, 26 Professors and 75 Lessons.

```bash
# From backend/ with its configured PostgreSQL connection:
python manage.py seed_academics
python manage.py seed_academics --prune --dry-run
python manage.py seed_academics --prune
```

For an already running Compose stack, use the equivalent command prefix:

```bash
docker compose --env-file .env.docker exec backend python manage.py seed_academics --prune --dry-run
```

Normal seed synchronizes the six catalog Sections, reuses Professor rows by exact trimmed name, and creates/updates Lessons by `(section_slug, title)`. The stable identity does not depend on database ID, professor or term. Repeated runs update changed catalog fields without duplicating matching Lessons. The default mode **never deletes** stale Lessons, Professors, Sections, users or Resources. Consequently, a populated database can contain more than the fresh-database catalog counts. Duplicate matches for a required professor name or catalog lesson identity stop the command with an error.

`--prune` adds explicit cleanup after catalog synchronization. A Lesson whose `(section_slug, title)` is not in the catalog is stale. The command deletes only stale Lessons with **zero Resource rows**. Stale Lessons with Resources are listed with their ID, title and Resource count, retained with their content, and reported as `PRUNE INCOMPLETE`. It then removes only Professors outside the catalog that no remaining Lesson references. It does not delete extra Sections. The execution uses a database transaction and locks existing Lessons while checking Resources; if a Resource appears before deletion, it aborts and rolls back. Direct lesson deletion through the staff API is different: that API intentionally cascades its Resources.

`--dry-run` is read-only. With `--prune`, it lists planned Lesson creates/updates, stale Lessons safe to delete, stale Lessons blocked by Resources, Professors safe to delete, and expected final counts. It does not guarantee those counts if data changes after the preview. **Always run `--prune --dry-run` first on an existing database, review every candidate, and take a PostgreSQL plus media backup before an approved real prune.** Do not assume final counts will be 6/26/75 when protected stale Lessons or extra Sections remain.

## Development data cleanup

`cleanup_dev_test_data` is for a verified development database only. It refuses to run unless `DEBUG=True`. Without `--yes`, it previews candidates and then raises a `CommandError`, so the preview command exits non-zero by design:

```bash
# From backend/; DEBUG must be true:
python manage.py cleanup_dev_test_data
# After reviewing that exact database and accepting the listed deletions:
python manage.py cleanup_dev_test_data --yes
```

It targets users whose `student_no` starts with `499`, Resources whose title is exactly `E2E-TEST-UPLOAD`, and `Test Prof` Professor rows only if no Lesson references them. The preview shows each candidate, whether a targeted Resource has a stored file, Professor reference counts, and retained Resources that would lose uploaded/reviewed-by attribution because user foreign keys use `SET_NULL`. `--yes` deletes the targeted rows in a database transaction. Stored-file deletion uses the normal post-commit signal. Do **not** change a production deployment to `DEBUG=True` to run this command.

## Lesson deletion and file cleanup

Staff `DELETE /api/lessons/{id}/` returns 204 after deleting the Lesson in a transaction. The Resource foreign key uses `CASCADE`, so related Resource rows are deleted too. The `post_delete` signal schedules file cleanup with `transaction.on_commit`; it checks whether another Resource still references the stored file before calling Django storage deletion. Unrelated Resources and shared files remain. Missing files do not block deletion. Unexpected storage failures are logged after commit, leaving a possible orphan for operator investigation without changing the successful database result. `--prune` is more conservative and never automatically deletes a stale Lesson that has any Resource.

## Checks, logs and test suite

```bash
# From backend/:
python manage.py check
python manage.py makemigrations --check
python manage.py showmigrations
python manage.py test
```

Runtime and tests require PostgreSQL; the configured database role needs permission to create the Django test database. There is no SQLite fallback. For the running Compose stack:

```bash
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs --tail=100 backend-init
docker compose --env-file .env.docker logs -f backend
docker compose --env-file .env.docker logs -f frontend
docker compose --env-file .env.docker exec backend python manage.py check
docker compose --env-file .env.docker exec backend python manage.py check --deploy
docker compose --env-file .env.docker exec backend python manage.py test
```

`check --deploy` is meaningful with the actual production environment. The backend container's health check probes `/api/health/`; the frontend checks `/healthz`. From the edge, probe both:

```bash
curl -f http://127.0.0.1:8080/healthz
curl -f http://127.0.0.1:8080/api/health/
```

Use the public HTTPS hostname instead of loopback after VPS deployment. Health checks do not replace the login/upload/moderation and admin smoke tests in [deployment](deployment.md#smoke-tests).

## Backup and restore

PostgreSQL is in the `postgres_data` volume; stored uploads are in `media_data`. A database dump **does not include uploaded files**. Back up both at a consistent point, keep copies outside Git, protect backup access, and periodically test restoration. This repository does not automate backups. Before a real `--prune`, lesson deletion or major upgrade, take a fresh backup and allow for a maintenance window.

A generic custom-format database dump through the current Compose `postgres` service, without publishing its port:

```bash
docker compose --env-file .env.docker exec -T postgres sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > backup.dump
```

The shell redirects the dump to a file on the host running Compose. Back up `media_data` separately with trusted volume/snapshot tooling at the same maintenance point. Preserve the pairing between dump and media snapshot. To rehearse a restore, create a separate empty test database and feed the dump to `pg_restore -U ... -d ... --no-owner`; verify both database records and stored media before depending on the backup.

A **destructive restore into the configured application database** is an operator-controlled maintenance action. Stop frontend/backend writes (for example, `docker compose --env-file .env.docker stop frontend backend`), verify the target database and backup, and only then use the matching stored-media snapshot and a command such as:

```bash
docker compose --env-file .env.docker exec -T postgres sh -c 'exec pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < backup.dump
```

`--clean` removes existing database objects before recreating dump contents. Do not run it against a live or unintended database. After restoring, restart the stack with `docker compose --env-file .env.docker up -d --wait`, inspect `backend-init` and migrations, then run the deployment smoke tests. PostgreSQL restoration alone does not restore `media_data`.
