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

Or add this repository as a skill tap:

```bash
hermes skills tap add vipul-sharma20/hermes-skill
hermes skills install vipul-sharma20/hermes-skill/<skill-name>
```

Hermes security-scans third-party skills before installation.

## Published skills

No skills have been published yet. They will be added and reviewed one at a time.

## License

MIT — see [`LICENSE`](LICENSE).
