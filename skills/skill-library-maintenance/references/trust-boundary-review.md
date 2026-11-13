# Privileged filesystem and subprocess review

These are threat-model and regression requirements, not a bundled implementation. Directory-descriptor/no-follow techniques are POSIX- and often Linux-specific; use a reviewed platform-native equivalent and test it rather than claiming Windows parity from prose.

Record actual identities/ownership, attacker-controlled inputs, protected outside files, allowed outputs and forbidden external calls. Inspect operator modules before importing them: top-level code can contact services or mutate state. Reuse reviewed safety primitives instead of inventing another security-sensitive implementation during an audit.

## Filesystem regressions

Use temporary managed trees and outside sentinels. Include existing/dangling symlinks, hardlinks, FIFO/special files, symlink ancestors and link swaps. Demonstrate the relevant outside mutation or unauthorized execution when reproducing a defect; a missing import is not a security regression. Bound special-file reads so the test cannot hang.

For privileged writers, path existence and resolve-check-reopen alone do not establish race-free containment. Pin ancestors/opened objects with suitable directory descriptors, no-follow/type/owner/link-count checks and expected metadata. Validate the full intended managed set before mutation. Use appropriately exclusive temporary files, verified metadata, atomic replacement and required file/directory syncing. Atomic file replacement does not make a multi-file installation transactional; define a fail-closed recovery policy and test partial state.

Generate private material only under a verified private parent, not a project-controlled destination. Export only validated public encoding/fingerprints. A filename suffix/comment is untrusted; public encoding validity does not prove correspondence to an intended private key. Never include private bytes in logs or rich assertion diffs.

## Hostile Git/subprocess probes

Dry-run/no-verify flags alone do not neutralize inherited Git config, hooks, remote helpers or environment. For an explicitly authorized isolation probe, use a fresh disposable repository with empty templates, scoped objects, validated refs/URLs, allowlisted environment/protocols and process-scoped config/hook restrictions. Keep normal user hooks and configuration unchanged; audit-only suppression must not persist into ordinary user operations.

Exercise hostile hooksPath/fsmonitor/sshCommand/pushurl/helper and environment cases against temporary repositories. Replace only forbidden transport with an audited local adapter and inspect the original command/environment before substitution. Assert no marker execution, unintended destination ref or normal-config change. This establishes only exercised local isolation, not cloud authentication or host-key readiness. State any mocked key generation or transport limitation explicitly, and retain failure in exit status instead of masking it behind a later successful command.
