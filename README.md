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
| [`kanban-task-management`](skills/kanban-task-management/SKILL.md) | Create and verify work items on the board the user actually named. |
| [`optimize-image`](skills/optimize-image/SKILL.md) | Compress images to byte and dimension limits with minimal quality loss. |
| [`indian-railways-pnr-monitor`](skills/indian-railways-pnr-monitor/SKILL.md) | Monitor RailYatri PNR status changes with silent-unless-changed cron jobs. |
| [`publish-note`](skills/publish-note/SKILL.md) | Publish GitHub-backed microblog notes with optional Cloudflare R2 images. |

Every skill is sanitized before publication. Live configuration, credentials, state files, personal PNRs, private workspace identifiers, and machine-specific paths are excluded.

## Testing

Run the complete offline suite with isolated dependencies:

```bash
uv run --with "pyyaml>=6,<7" --with "pillow>=11,<13" \
  --with "pillow-heif>=1,<2" --with "boto3>=1.40,<2" \
  python -m unittest discover -s tests -v
```

## License

MIT — see [`LICENSE`](LICENSE).
