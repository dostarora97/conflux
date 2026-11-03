# Conflux

A shared design library for a Git-first agent communication protocol, developed through independent peer review by **tpp-claude** and **git-protocol-codex**.

## Start here

Read the [single self-contained design specification](spec/git-coordination-spec-reviewed-v2-0dd7b392.md). It includes the algorithm, observation and crash tables,24 base traces,T25/T26 extensions, encoding recommendation, optional harness guidance, and preserved architecture alternatives.

Endorsed SHA-256: `0dd7b3922981abce73c83e9f9ad2ca4cc6a036647eff51e796f98a5196c30a65`. The [verification record](spec/git-coordination-spec-reviewed-v2-0dd7b392.verification.json) identifies the six unchanged embedded sources. Pending headers within those snapshots are historical publication metadata; later endorsements establish their review scope.

For a shorter introduction: [vocabulary and worked example](orientation/semantic-algorithm-reader-guide-v2.md), or [narrative orientation](orientation/tpp-algorithm-in-plain-terms-v2.md).

## Status and direction

This is a jointly reviewed **design draft and recommendation**. The interoperable grammar is not frozen; no protocol implementation or1000-agent capacity validation is delivered here.

The recommendation uses one communication repository, separate from code repositories, with independent per-channel/per-writer streams. Writers retain intents and reconcile uncertain publication against the target stream. Readers retain verified observations and recoverable pending work. Scan/ingestion can advance before application handling when recovery is assured; handling progress requires qualifying dispositions.

The preferred model separates record identity from publication occurrence. Record trees are the current default recommendation; compact commit-as-record and parentless record-commit wrappers remain alternatives. The described authority baseline serializes order-sensitive transitions, while other explicit profiles can define their own invariants. The core supplies no generic exactly-once external-effect guarantee; an application/provider may supply a stronger scoped contract.

## Library map

| Location | Purpose and scope |
|---|---|
| [spec](spec/) | Pinned consolidated design and byte verification; appendix authority is topic-scoped. |
| [components](components/) | Algorithm/T25,24 traces,D.3 recommendation,T26 clarification and optional harness. Recommendations remain recommendations; optional guidance is not core by inclusion. |
| [decisions](decisions/) | Architecture basis and preserved alternatives, refined by later algorithm/D.3/T26 clauses. |
| [orientation](orientation/) | Endorsed explanations, not replacement contracts. |
| [alternatives](alternatives/) | Exact construction proposals; importing them selects no final grammar. |
| [background](background/) | Informative prior art and historical research; earlier claims may be corrected by the current design. |
| [evidence](evidence/) | Scope-limited local research scripts/results, not throughput proofs or a portable runtime. |
| [PROVENANCE.json](PROVENANCE.json) | Original/project paths, raw hashes, review scopes and approval snapshots. |
| [Import review](reviews/initial-import-codex-v1.md) | What was independently checked. |

## Continuing the design

Engineering can draft a grammar/profile under stated assumptions. Material inputs include host capabilities, retention/offline-lag expectations, message rates/sizes, overlap and desired latency. This is not a per-field human approval gate.

Preserve imported endorsed snapshots. A changed payload has a different review identity and needs its own stated review scope; future drafts can use versioned proposals and Git history under the human's instructions. This README supplies orientation and navigation, not another protocol contract.
