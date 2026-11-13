# Portable release packaging and parity

A skill supplies a reusable procedure and optional references/scripts/templates. Runtime tool, provider, hook or UI registration needs the corresponding supported integration. A procedure-only package must say that it does not ship an implementation or activate a capability merely by being installed.

## Package closure

Use the target repository's conventions; a community tap commonly has a root README/LICENSE and `skills/<name>/SKILL.md`. Do not run core-repository website generators in an unrelated tap. Keep SKILL.md canonical rather than adding redundant package READMEs.

Check real YAML metadata, concise description, version, intentional human-first authorship, licence, audited platforms and resolvable related skills. Reference every required support file explicitly and test transitive local links. Avoid private layout dependencies; a variable-expanded command is not proof that a clean installation can find a helper. Keep configuration templates invalid until intentionally configured and fixtures wholly synthetic.

Installing a procedure does not authorize account setup, deployment or publication. Prefer native supported installers in a disposable isolated home when that test is authorized; enumerate installed files and exercise only non-destructive help/tests. Preview, source copying and relocated-file checks are not native-install proof. Inspect both installed CLI help and current official docs before stating a resolver contract.

## Safe consumer boundaries

Transport arbitrary user input with request files or reviewed argv, not interpolation inside a shell string. Exercise quotes, semicolons, backticks and command-substitution literals as inert data. Credentials dedicated to an optional feature must be optional in actual readiness logic and explicitly passed to clients; metadata alone may not enforce this. Never silently fall back to ambient cloud credentials.

Trace the complete caller chain. For media compare encoder capability/defaults, caller format selection, decoded bytes, filename extension and MIME. For monitors compare parser identity/counts, normalization, fingerprint, formatting, state, delivery and acknowledgement separately. A transport difference is not automatically missing parser behavior.

## Offline parity

Record exact source roots/revisions and baseline scope. Distinguish byte identity, tested fixture equivalence, intentional policy difference, functional gap and unresolved behavior. A version, timestamp or manifest alone proves neither ownership nor improvement.

Inspect top-level imports and live-call guards before tests. Use the documented dependency bounds with temporary/bytecode/cache writes in approved scratch. Dependency-manager offline mode does not prevent tested code from opening sockets. Prefer recording fakes without constructing real service clients. Isolate same-named helper imports so caches cannot make two implementations accidentally share code. Preserve public validation, bounded subprocesses, credential isolation and atomic state while porting only a demonstrated improvement.

## Release gates

Scan exact final outbound bytes and all outbound history, not only added lines. Review ownership/redistribution for supporting files too; locally installed material is not automatically original or redistributable. Run package-specific regression tests, native security checks where available, privacy checks and a fresh independent release review. Explain warnings individually; concrete dangerous findings block release. Do not weaken a guard or globally exempt a value to obtain a clean report.

Commit, history cleanup and push require their own authorization. Verify the intended destination and exact remote ref/content after an authorized push. Static tests, native installation, remote installation and live integration are separate gates; report unrun gates rather than inventing success.
