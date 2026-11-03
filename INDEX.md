# conflux — canonical shared library

A git-native agent-coordination protocol: a single communication-only repository where ~1000 globally-distributed agents coordinate via topic-scoped per-(channel, writer) streams. Design produced by two independently-invoked peer agents (`tpp-claude` + `git-protocol-codex`) through adversarial review.

**Name:** *conflux* — many agent streams flowing together (cohesive with the channel / stream / frontier vocabulary).

**Status (honest):** a jointly-endorsed **recommendation + principles**, NOT an implemented protocol, NOT a frozen wire grammar, NOT a validated 1000-agent/WAN/throughput capacity. A genuine counterexample or real cost evidence can revise any recommendation here.

---

## Start here

- **[`spec/git-coordination-spec-reviewed-v2-0dd7b392.md`](spec/git-coordination-spec-reviewed-v2-0dd7b392.md)** — the single self-contained consolidated spec (informative front matter §0–13 + appendices A–F carried inline). Endorsement binds the pinned bytes: **SHA256 `0dd7b3922981abce73c83e9f9ad2ca4cc6a036647eff51e796f98a5196c30a65`**.
  - [`spec/codex-consolidation-appendix-contribution-v1.manifest.json`](spec/codex-consolidation-appendix-contribution-v1.manifest.json) — per-appendix source markers + byte lengths + SHA-256.
  - [`spec/git-coordination-spec-reviewed-v2-0dd7b392.verification.json`](spec/git-coordination-spec-reviewed-v2-0dd7b392.verification.json) — codex's verification record.

## Layout and per-item authority (topic-scoped, NOT a blanket "governs")

| Path | Contents | Authority scope |
|---|---|---|
| [`spec/`](spec/) | the consolidated spec (appendices inline) + manifests | the one-file entry; authority is **per appendix** (below), not uniform |
| [`components/`](components/) | the governing source artifacts the spec embeds (original filenames, so the manifest verifies) | **A** algorithm ([`codex-algorithm-review-v2.md`](components/codex-algorithm-review-v2.md), incl. T25) and **B** traces ([`semantic-trace-suite-v2-peer-reviewed-draft.md`](components/semantic-trace-suite-v2-peer-reviewed-draft.md)) and **D** retention/T26 ([`reader-retention-clarification-T26-v1.md`](components/reader-retention-clarification-T26-v1.md)) are **normative within their stated scopes**; **C** encoding ([`encoding-recommendation-D3-v1-codex-draft.md`](components/encoding-recommendation-D3-v1-codex-draft.md)) is a **recommendation** (final grammar open); **E** ([`codex-optional-attention-harness-note-v2.md`](components/codex-optional-attention-harness-note-v2.md)) is an **optional** capability layer |
| [`decisions/`](decisions/) | [`git-coordination-decision-record-v3.md`](decisions/git-coordination-decision-record-v3.md) — architecture + §C preserved alternatives | architecture governing; alternatives informative |
| [`orientation/`](orientation/) | [`tpp-algorithm-in-plain-terms-v2.md`](orientation/tpp-algorithm-in-plain-terms-v2.md), [`semantic-algorithm-reader-guide-v2.md`](orientation/semantic-algorithm-reader-guide-v2.md) | informative on-ramps |
| [`background/`](background/) | prior-art lessons + semantic distinctions (Matrix/SSB/Yjs/Nostr/git-bug/Radicle/Lamport/XMPP) | informative |
| [`evidence/`](evidence/) | scope-limited local test scripts + results | evidence, NOT scale proofs |

## The design in one breath

One comms-only repo. Each writer appends to its own single-writer **stream** within a **channel** (rooms, DMs, broadcast, role-request queues are channel *uses* with possibly different policies). Readers fetch the channels they care about, pin the exact fetched OID, classify against a durable verified observation (tri-state ancestry + a distinct genesis-identity-conflict case), and advance **stage-scoped cursors**: a scan/ingestion cursor may advance with recoverable pending work retained, while a handling cursor advances only through qualifying handled dispositions (holes preserved). Record identity is separated from publication-occurrence identity (record-tree default; alternatives preserved). Authority/membership is an **optional** profile — the core has **no mandatory shared-application authority state machine**; in the described **baseline** authority profile, authoritative order-sensitive policy changes go through a single serialization point rather than a multi-writer merge (this is the baseline's choice, **not** a universal ban on an explicitly specified future mergeable-data profile). Retain-all by default. Honest edges throughout: the **core** provides **no generic exactly-once external effect** (a specific provider/application may, under its own contract), no bounded latency, and "unknown" is carried rather than guessed.

## Open items

The final interoperable grammar/profile is **engineering-draftable under stated assumptions** — it is **not** a per-field human-approval gate. The *material inputs we lack* are: (1) human priorities; (2) actual host capabilities (consistency model, linear-history/ruleset, partial-clone/promisor availability, rate limits); (3) measured workload budgets (latency, message rate/size, overlap, polling); and (4) the retention/fencing profile + host admission mechanism actually available. The next engineering step, once those exist, is a candidate grammar/profile draft under stated assumptions.

## Working in this repo

Shared by both agents (`tpp-claude` + `git-protocol-codex`); either may edit and commit. **git gotcha:** the global pre-commit hook fails closed via `gh`, and `GH_HOST` may be set to a non-matching host — run `env -u GH_HOST git commit/push …` for conflux git ops. Coordinate to avoid push races (pull/`--rebase` before push; announce intent in the peer session).

## Provenance

Full derivation trail, superseded drafts, review exchanges, and ledgers live in the peer session `~/.agents/chats/sessions/20261102T185809Z-dc0b44f5-3740-496f-836c-a5216e853629/` and the append-only research ledgers (tpp: `~/personal/code/claude_agent-coordination-research/research-ledger.md`; codex: `~/personal/code/agent-coordination-research/`). Files here are curated copies with original filenames preserved (so the appendix manifest/hashes verify); the session retains the pinned endorsement snapshots. (codex is adding `README.md` + `PROVENANCE.json` + the detailed encoding-alternatives/original-research sources omitted from the curated import.)
