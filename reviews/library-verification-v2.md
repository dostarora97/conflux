# Conflux library verification — v2

Prepared by git-protocol-codex, 2026-11-03 UTC. Follow-up to [the initial import check](initial-import-codex-v1.md); that earlier note remains unchanged.

## Published import

Commit `f4a5b9799d71d4f76445c0e02f6e5dcc438b6cd7` added navigation, provenance, two encoding alternatives and four historical research/evidence sources to the initial curated library. The pre-existing peer commits are preserved. All 34 imported source payloads matched their original paths, byte lengths and SHA-256 values. The seven allowlisted approval snapshots in [PROVENANCE.json](../PROVENANCE.json) matched their original messages and raw hashes. README relative links and staged whitespace checks passed. No endorsed source was edited.

The push to origin/main succeeded; a subsequent remote-ref query returned the same full commit identity. The worktree was clean at verification. GitHub metadata reported the repository public. The human explicitly confirmed that the **design library should remain public**; this is separate from the deployed private communication-repository premise.

Installed Git hooks remained active. Command-scoped GitHub host selection matched the github.com origin. Entire reported disabled/not set up for this repository. A previously reported accidental environment dump was excluded from this import and from the selected provenance snapshots. This records specific checks, not a general credential audit or a claim that credential rotation has occurred.

## Independent peer review

The [exact peer approval message](import-approval-tpp-v1.json) was copied byte-for-byte from `/Users/I533118/.agents/chats/sessions/20261102T185809Z-dc0b44f5-3740-496f-836c-a5216e853629/2026-11-03T061521Z-6a3e3278-tpp-claude.json`.

SHA-256: `e577b4378aaef7f30ca3b4d3d9cc48d934d54087ac99cf57098bf26bafc4a9b9`.

The peer independently approved the navigation/provenance import and confirmed that its artifact-specific endorsements were accurately preserved. This review concerns the import and its attribution. It does not promote historical alternatives, informative orientation or optional guidance into mandatory protocol requirements.

The canonical endorsed specification remains [reviewed v2](../spec/git-coordination-spec-reviewed-v2-0dd7b392.md), SHA-256 `0dd7b3922981abce73c83e9f9ad2ca4cc6a036647eff51e796f98a5196c30a65`. Grammar, implementation and hosted capacity validation remain open.
