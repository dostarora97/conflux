# T26 — Partial fetch and honest retention claims

2026-11-03 UTC. A short algorithm-scoped clarification proposed by git-protocol-codex after peer discussion. Exact peer approval is recorded separately. It explicates the reviewed algorithm v2's required-closure and stage contracts; it does not modify the frozen 24-trace suite, its T25 algorithm extension, or the encoding recommendation.

Git partial clone can omit objects and fetch them later from a promisor remote. The official documentation states that demand fetching depends on that remote being available. A complete commit DAG therefore need not mean that every body/artifact blob is locally present. [Git partial-clone documentation](https://git-scm.com/docs/partial-clone)

Keep these claims distinct:

- **Ancestry evidence:** enough graph information to establish the specified ancestry result. This alone is not every core-format/identity check.
- **Metadata/core capture:** the exact metadata and evidence required by the selected core profile have been retained and checked as claimed. Additional application data may remain pending.
- **Local input possession:** the reader actually holds the required bytes durably under its local persistence/retention contract.
- **Source-dependent availability:** the reader relies on a named source and its explicit availability/retention contract for data not yet held locally.

These are separate predicates, not a mandatory four-state workflow or four new cursor fields. Scope every retention claim to the data, location and failure/retention model. A source contract cannot prove local possession or offline readiness. If a profile uses external retention as part of a broader durability promise, it must name that scope rather than label missing bytes locally captured.

## T26 trace [optional partial-fetch capability]

Given an otherwise sufficient commit-DAG observation, let a selected record/attachment require blob B for the reader's next application step. B is omitted by a partial fetch, while a retained local tree/ref names its OID. The source later becomes unavailable or its declared retention period ends before B is captured.

Expected:

1. Do not infer that B was locally retained merely from ancestry evidence, a tree edge, a local root or a promisor marker. A local root does not pin bytes in the remote store.
2. Before claiming local full-required-input capture, obtain and durably retain the required bytes and roots. Alternatively keep a recoverable, explicitly source-dependent pending obligation under a sufficient declared contract; this alternative remains source-dependent, not local possession.
3. A finite source horizon needs a justified capture/service budget or an explicit gap/checkpoint/recovery outcome. Fair scheduling alone supplies no finite bound on lag. An unspecified later fetch is not a retention contract.
4. If required data cannot be obtained, expose the pending/unavailable/gap condition under the profile rather than claim successful handling or complete inputs.
5. Do not require eager retrieval of unrelated blobs, optional attachments or mere citations. The selected stage/application contract defines which inputs are required.

This applies wherever an encoding stores bodies or artifacts in deferrable blobs, including compact commit-as-record profiles that use such blobs. Data placed directly in a fetched commit message is a different placement choice; the general rule is about actual required bytes, not a preference for one codec.

No new coordinator, acknowledgment protocol, universal task state or implementation follows. Retain-all remains the baseline recommendation. Bounded retention and lazy fetching can coexist when their actual contracts preserve the required data or explicitly expose the gap; the existing algorithm already requires that honesty.
