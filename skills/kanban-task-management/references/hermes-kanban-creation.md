# Hermes Kanban Creation Notes

## Board selection

When the user names Hermes Kanban, use the native Hermes Kanban board directly. Do not ask for an external board URL or reinterpret the request as a GitHub issue.

## Record shape

A useful migration card can use:

- title: `Move database from SQLite to PostgreSQL`
- body: schema and DDL planning, application configuration and data-access updates, existing-data migration, tests, and production-readiness validation
- status: the normal intake state (`todo`) unless the user specifies another column
- creator: the current user or session when available
- assignee, due date, priority, project, and branch: unset unless explicitly provided

## Verification

After creation, retrieve the card and verify its stable ID, title, body, status, and creator. If creation times out or the result is unclear, search by title before retrying. Keep the user-facing confirmation concise.

## General failure pattern

A named destination is sufficient context when the native board is available. Searching for an unrelated repository or asking for an external URL introduces needless ambiguity and can create the item in the wrong system.
