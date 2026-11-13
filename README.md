# Hermes Skill

A collection of reusable skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

> [!NOTE]
> This repository is mostly written and managed by a Hermes Agent. The skills, scripts, documentation, tests, and maintenance changes are primarily produced with agent assistance rather than being entirely handwritten. Human oversight is used for publishing decisions, credentials, privacy-sensitive data, and final approval.

## Repository structure

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── scripts/       # Optional helper scripts
    ├── references/    # Optional supporting documentation
    ├── templates/     # Optional reusable templates
    └── assets/        # Optional static assets
```

`SKILL.md` is the canonical documentation and installation entry point for each skill. Individual skill directories do not need a separate `README.md` unless they require extended examples or documentation intended primarily for people browsing on GitHub.

## Installing a skill

Install one skill directly:

```bash
hermes skills install vipul-sharma20/hermes-skill/skills/<skill-name>
```

Or add this repository as a skill tap, then install with the tap-qualified identifier:

```bash
hermes skills tap add vipul-sharma20/hermes-skill
hermes skills install vipul-sharma20/hermes-skill/<skill-name>
```

Hermes security-scans third-party skills before installation.

## Published skills

| Skill | Purpose |
|---|---|
| [`skill-library-maintenance`](skills/skill-library-maintenance/SKILL.md) | Audit learning, consolidate proposal backlogs, and review portable releases with reversible changes. |
| [`state-change-monitoring`](skills/state-change-monitoring/SKILL.md) | Design bounded change-only monitors with last-good state and explicit delivery semantics. |
| [`self-hosted-operations`](skills/self-hosted-operations/SKILL.md) | Diagnose and maintain shared Linux hosts with evidence, scoped changes, and rollback. |
| [`licensed-media-curation`](skills/licensed-media-curation/SKILL.md) | Verify image identity, image-specific rights, integrity, and useful visual coverage. |
| [`container-storage-migration`](skills/container-storage-migration/SKILL.md) | Plan and verify Docker storage moves with backup, ownership, and recovery checks. |
| [`amp-hermes-mcp`](skills/amp-hermes-mcp/SKILL.md) | Connect Amp to scoped Hermes consultation and separately approved action requests. |
| [`amp-self-hosted-orbs`](skills/amp-self-hosted-orbs/SKILL.md) | Run Docker-backed Amp orbs with scoped lifecycle handling and resource ceilings. |
| [`kanban-task-management`](skills/kanban-task-management/SKILL.md) | Create and verify work items on the board the user actually named. |
| [`optimize-image`](skills/optimize-image/SKILL.md) | Compress images to byte and dimension limits with minimal quality loss. |
| [`indian-railways-pnr-monitor`](skills/indian-railways-pnr-monitor/SKILL.md) | Monitor RailYatri PNR status changes with silent-unless-changed cron jobs. |
| [`indian-railways-running-status-monitor`](skills/indian-railways-running-status-monitor/SKILL.md) | Monitor train location, delay, ETA, and arrival with change-only alerts. |
| [`publish-note`](skills/publish-note/SKILL.md) | Publish GitHub-backed microblog notes with optional Cloudflare R2 images. |

Every skill is sanitized before publication. Live configuration, credentials, state files, personal PNRs, private workspace identifiers, and machine-specific paths are excluded.

The maintenance, monitoring-design, self-hosted-operations, licensed-media-curation, and storage-migration packages are **procedure-only**. They provide instructions and bundled reference contracts, not deployed collectors, migration executables, or automatic publication. Loading them grants no operational permissions. Publication-audit guidance is included in the maintenance package rather than a separate overlapping skill.

The Amp skills document reusable setup and verification workflows, not a copy of a personal deployment. `amp-hermes-mcp` does not bundle a running MCP server. Installing either skill only makes its instructions and bundled files available; it does not register an account integration, start services, or change a host. Those operations require the operator's authorized setup and verification.

## Testing

Run the complete offline suite with isolated dependencies. Tests do not register Amp integrations or start providers; the orb dispatcher's Docker boundary is exercised with a fake CLI, not a live Docker daemon or Amp account.

```bash
uv run --with "pyyaml>=6,<7" --with "pillow>=11,<13" \
  --with "pillow-heif>=1,<2" --with "boto3>=1.40,<2" \
  python -m unittest discover -s tests -v
```

## License

MIT — see [`LICENSE`](LICENSE).
