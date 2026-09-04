---
name: kanban-task-management
description: "Use when creating or managing Kanban work items."
version: 0.1.0
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Kanban, Task-Tracking, Work-Queues, Ticketing]
    related_skills: []
---

# Kanban Task Management

Create, route, and verify work items on a Kanban board without silently redirecting them to a different tracker.

## When to Use

Use when a user asks to create, add, move, or manage a ticket or work item on a Kanban board, including a native Hermes Kanban board.

Don't use when the user explicitly asks for a GitHub issue, Notion record, or another tracker; use that system's dedicated workflow instead.

## Core Principles

- Treat the user's requested board as the destination, not as a request to create an external GitHub issue unless they explicitly name GitHub.
- Convert a short request into a useful, implementation-oriented title and concise acceptance-oriented description without inventing owners, deadlines, priorities, or estimates.
- Prefer the board's supported CLI, API, or Hermes tool interface. If a lower-level interface is required, preserve the same schema and verify the resulting record by reading it back.
- Report the destination, status, and stable task identifier after a successful write.

## Procedure

### 1. Identify the destination

Determine which board owns the work. If the user names a system such as Hermes Kanban, use that system directly. Ask only when the destination genuinely remains ambiguous. Done when exactly one target board is selected.

### 2. Normalize the request

Create:

- a concrete title using an action and target, such as `Move database from SQLite to PostgreSQL`;
- a short body covering scope and observable completion criteria;
- the board's normal intake status when no status is specified;
- no invented assignee, due date, priority, project, or branch.

For a migration request, include schema and data migration, application configuration and data-access changes, existing-data migration, tests, and production-readiness validation when naturally implied. Done when every requested field is represented and unsupported metadata remains unset.

### 3. Search before creating

Check for an existing matching open item using the board's search or list capability. If an exact or near duplicate exists, present it instead of silently creating another card. If the user explicitly requests a new ticket despite a duplicate, create it and state that choice. Done when duplicate handling is explicit.

### 4. Create through the board interface

Use the supported Kanban command or Hermes tool for the named board. Set the creator to the current user or session when supported. Keep the initial state in the board's normal intake column unless the user specifies another column. Done when the interface returns a stable item identifier or a verifiable pending result.

### 5. Verify the write

Read back the created item and check at minimum: stable ID, title, body or description, status or column, creator, and explicitly requested metadata. Do not claim success from an exit code alone. If the result is ambiguous, search by title or idempotency marker before retrying. Done when the read-back matches the request.

### 6. Respond concisely

Return the title, status, board, and stable ID. Mention assumptions, omitted metadata, or duplicate detection. Do not include implementation details unless requested.

## Pitfalls

- Asking for a board URL after the user already named a native board.
- Creating a GitHub issue when the user requested a Kanban card.
- Turning a terse request into an over-specified ticket with fabricated ownership or deadlines.
- Reporting an item as created without reading it back.
- Retrying a timed-out creation before searching for the original result.
- Capturing a one-off database path or local command as the general workflow.

## Verification

- [ ] Correct board selected from the user's wording.
- [ ] Title is concrete and the body has actionable scope.
- [ ] No unsupported owner, due date, priority, or estimate was invented.
- [ ] Duplicate search was performed when the interface permits it.
- [ ] Created item was read back and its ID and status were verified.
- [ ] Confirmation includes the destination and stable identifier.

For Hermes-specific mappings, read `references/hermes-kanban-creation.md`.
