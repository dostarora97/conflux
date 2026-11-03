# conflux — canonical shared library

A git-native agent-coordination protocol: a single communication-only repository where ~1000 globally-distributed agents coordinate via topic-scoped per-(channel, writer) streams. Design produced by two independently-invoked peer agents (`tpp-claude` + `git-protocol-codex`) through adversarial review.

**Name:** *conflux* — many agent streams flowing together (cohesive with the channel / stream / frontier vocabulary).

**Status (honest):** a jointly-endorsed **recommendation + principles**, NOT an implemented protocol, NOT a frozen wire grammar, NOT a validated 1000-agent/WAN/throughput capacity. A genuine counterexample or real cost evidence can revise any recommendation here.

---

## Start here

- **`spec/git-coordination-spec-reviewed-v2-0dd7b392.md`** — the single self-contained consolidated spec (informative front matter §0–13 + normative exact-byte appendices A–F). Endorsement binds the pinned bytes: **SHA256 `0dd7b3922981abce73c83e9f9ad2ca4cc6a036647eff51e796f98a5196c30a65`**.
  - `spec/codex-consolidation-appendix-contribution-v1.manifest.json` — per-appendix source markers + byte lengths + SHA-256.
  - `spec/git-coordination-spec-reviewed-v2-0dd7b392.verification.json` — codex's verification record.

## Layout

| Folder | Contents | Authority |
|---|---|---|
| `spec/` | the consolidated spec (appendices carried inline) + manifests | the spec is the one-file entry; per-appendix topic-scoped authority |
| `components/` | the governing source artifacts the spec embeds | normative within scope: algorithm (`codex-algorithm-review-v2.md`, incl. T25), traces (`semantic-trace-suite-v2-peer-reviewed-draft.md`), **encoding recommendation** (`encoding-recommendation-D3-v1-codex-draft.md`), **T26 retention** (`reader-retention-clarification-T26-v1.md`), optional attention/harness (`codex-optional-attention-harness-note-v2.md`) |
| `decisions/` | `git-coordination-decision-record-v3.md` — architecture + §C preserved alternatives | architecture governing; alternatives informative |
| `orientation/` | `tpp-algorithm-in-plain-terms-v2.md`, `semantic-algorithm-reader-guide-v2.md` | informative on-ramps |
| `background/` | prior-art lessons + semantic distinctions (Matrix/SSB/Yjs/Nostr/git-bug/Radicle/Lamport/XMPP) | informative |
| `evidence/` | scope-limited local test scripts + results | evidence, NOT scale proofs |

## The design in one breath

One comms-only repo. Each writer appends to its own single-writer **stream** within a **channel** (rooms, DMs, broadcast, role-request queues are channel *uses*). Readers fetch the channels they care about, pin the exact fetched OID, classify against a durable verified observation (tri-state ancestry + a distinct genesis-identity-conflict case), and advance stage-scoped cursors (scan/ingestion vs handling) only through recorded dispositions. Record identity is separated from publication-occurrence identity (record-tree default; alternatives preserved). Authority/membership is an **optional** profile — the core has no mandatory shared-application state machine; authoritative policy changes go through a single serialization point, never a multi-writer merge. Retain-all by default; honest edges throughout (no exactly-once effects, no bounded latency, "unknown" carried not guessed).

## Open items (need human / profile inputs)

1. The final interoperable encoding cut + exact grammar.
2. Retention/fencing profile + the host admission mechanism actually available.
3. Host consistency model (one authoritative conditional-write history per stream; not independent writable mirrors).
4. Real-host workload budgets (latency, message rate/size, overlap, polling).

Next engineering step, once those inputs exist: a candidate grammar/profile draft under stated assumptions.

## Provenance

Full derivation trail, superseded drafts, review exchanges, and ledgers live in the peer session `~/.agents/chats/sessions/20261102T185809Z-dc0b44f5-3740-496f-836c-a5216e853629/` and the append-only research ledgers (tpp: `~/personal/code/claude_agent-coordination-research/research-ledger.md`; codex: `~/personal/code/agent-coordination-research/`). Files here are curated copies with original filenames preserved (so the appendix manifest/hashes still verify); the session retains the pinned endorsement snapshots.
