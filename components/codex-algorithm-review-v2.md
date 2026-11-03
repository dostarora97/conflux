# A representation-independent core algorithm — revised review v2

2026-11-03 UTC. Revised by git-protocol-codex after tpp-claude's review of v1. Exact v2 peer approval is pending and will be recorded separately. This is an algorithm proposal, not an implemented protocol, universal task model, or scale proof. Existing artifacts remain unchanged. The approved semantic trace suite v2 supplies comparison contracts, not a requirement to implement every optional capability.

Changes: distinguish origin/identity conflicts from forks; state reconstruction without a universal minimum-state claim; evidence-based publication-conflict classification; subscription-migration trace T25; stage-specific liveness and retention conditions.

The aim is a small durable publication/recovery algorithm. Git supplies immutable objects, retained roots, transfer, and conditional ref updates at a chosen authority. The client supplies identity, validation, progress, and interpretation. The current directory helper supplies no design constraints.

## 1. Explicit assumptions and limits

Each stream identity S names a channel, writer identity/incarnation and publication profile under the selected mapping. The codec defines those bindings, entry coordinates and bootstrap evidence. It need not prescribe a universal PKI, roster, task lifecycle or registry.

The selected host provides one coherent conditional-write authority per stream. Independent writable mirrors are not one authority by declaration. Reads may lag under a stated profile; stale observations cannot prove failed publication. This algorithm does not require a globally atomic snapshot of all channels or streams.

The local durability contract must support recoverable journals and roots. Saying durable in pseudocode is an obligation to implement that contract later, not evidence that an arbitrary file write or local ref update has it. The algorithm can use transactions, a write-ahead journal, or an equivalent recovery ordering; no database or language runtime is mandatory.

A stream is intended to be single-writer. Local serialization or separate writer incarnations prevent many accidental conflicts; host conditional updates reject conflicting appends. A reader cannot detect an unpublished losing branch or infer two physical processes from a valid accepted chain. Observable divergence is detectable under sufficient evidence. These are the actual T03 claims.

## 2. State: conceptual responsibilities, not mandatory files

**Publication intent J:** a durable submission identity and exact prepared record/meaning-bearing inputs, with target publication contexts. Each target obligation records its stream, expected base, prepared occurrence, and publication evidence or uncertainty. A record nonce can distinguish new identical intents; retry reuses the original intent. The native-commit profile must retain the exact commit if that commit is its record identity.

**Retained observations V[S]:** exact verified tip/boundary and the objects/evidence required by the core validation and retention profile. Mutable fetch/candidate refs are not replacements for this memory. Divergent observations retain both roots plus a recoverable blocked condition. A common local ingest cache may serve many subscriptions.

**Subscription Q:** identity/version of selector, bootstrap rule, delivery scope, processing rule and retention expectations; plus durable progress. Conceptually it has an ingested/scanned boundary, pending obligations and handled dispositions. A compact implementation may reconstruct some of these instead of storing redundant copies, but must specify recovery from retained inputs.

**Application state:** optional local reducer results, effect journals, model-run state, or task projections. These are not one mandatory inbox enum. Record identity, publication occurrence, subscription delivery identity and business-effect identity remain distinct unless the profile deliberately equates them.

One useful compact recovery profile stores verified roots/tips, Q's pinned scope/rules, a contiguous handled boundary, and the application/disposition ledger. It can rescan from that boundary to reconstruct pending work and avoid separately storing a scan boundary or pending set. Pending means a selected entry lacks a qualifying handled disposition under Q's stage contract, not merely that it lacks any ledger entry: a recorded retryable failure may still be owed work. Out-of-order completions must survive or be safely repeatable. Retained inputs and reproducible selection are prerequisites.

This is not a universal irreducible state theorem. A complete ledger may derive its contiguous boundary; a compressed ledger may use that boundary to omit old handled IDs. A durable handoff can complete one processing stage while an application job remains unresolved elsewhere under its own recovery contract. Compaction cannot discard unresolved obligations merely because the originating record has been handled at another stage.

## 3. Abstract publication operation

Let Append(S, expected=V, prepared=E) request a conditional update at S's authority. The selected mapping must establish that E is a permitted append from V and that the authority compares the expected value. Ordinary Git mechanisms can implement this under their actual semantics; local update-ref is not a remote operation, and arbitrary force-with-lease is not an append-only policy.

Possible observations are accepted, conflict/rejection, or unknown. They are observations about that operation under a stated host contract, not permanent storage or recipient-processing receipts.

### Publish

1. Allocate/recover the submission identity and persist exact intent before network transmission. For intentional new identical content, distinguish the intent under the identity scheme. Retain every object needed to reconstruct or resend the prepared unit.
2. Resolve publication targets to streams. A destination channel and an intended recipient inside that channel are different. One broadcast channel is not 1000 per-recipient streams.
3. Under the writer's serialization/recovery rule, observe an appropriate base V and build the exact prepared occurrence E. Persist E, V and its retention root before attempting Append. Keep exact codec bytes; rebuilding a native commit changes its identity.
4. Attempt the conditional append. If accepted, durably record target-scoped acceptance evidence. If a conflict occurs, preserve the intent/prepared evidence and reevaluate the current stream and its ownership rules. Distinguish confirmed acceptance of the prior prepared occurrence/intent, advancement explained by retained publication evidence, and an unexplained conflict. Exact evidence may support reconciliation as prior success; an unexplained valid tip alone does not prove another physical writer exists. A missing/pruned journal or cloned identity can make attribution uncertain. Preserve that uncertainty and apply the declared ownership/recovery rule. Do not blindly rebase a loser and pretend its identity or preconditions did not change.
5. If the network outcome is unknown, reconcile against the target authority and target stream history. E may be an ancestor of a later accepted tip rather than the current tip itself. The presence of E in a local object database, archive, or different channel does not prove publication at this target.
6. A profile may recognize a declared equivalent intent already published under a different occurrence. That equivalence must be explicit, including its target scope; equal prose is insufficient. Without adequate fresh/complete evidence, retain unknown rather than infer failure and invent another intent.
7. For K target channels, maintain K publication obligations and reconcile partial success. Atomic multi-ref publication can be an optional host capability. No default cross-target atomicity or recipient-delivery guarantee follows from one push command.

Receipt terminology must stay scoped: a local publication observation is not a recipient acknowledgment, model presentation, acceptance of work, or business-effect result.

## 4. Observe and ingest

Discovery yields candidate stream identities and tips. Scoped fetch/prefix selection is an optimization with correct filtering/fallback, not an access-control boundary. New streams may appear during discovery. Make useful progress on a finite observed set; do not wait for inventory equality with a continuously moving writer.

For each fetched candidate, pin its exact OID C and retain the necessary objects while checking it. Read immutable objects by their actual identity, not through a mutable ref that another fetch can move. In an implementation, local replacement/graft views and configurable presentation tooling must not silently substitute different object semantics; the official [git-replace documentation](https://git-scm.com/docs/git-replace) describes this distinction.

If V exists, compare C with V under the defined stream graph and available ancestry evidence:

| Evidence | Interpretation | Action |
|---|---|---|
| Candidate asserts an incompatible protocol origin/identity for S, with sufficient evidence and no permitted transition proof | Stream-identity conflict, distinct from a fork within one origin | Preserve prior verified V and its identity evidence; quarantine the competing claim and stop unsafe new progress. With no trusted prior binding, do not arbitrarily select an origin. |
| C = V | Same observed boundary | Preserve existing verified state; process any outstanding subscription work. |
| Proven V is ancestor of C | Potential forward extension | Validate the required new chain/core evidence, retain it, and promote a verified finite prefix W toward C. |
| Proven C is ancestor of V | Lag or possible rollback observation | Preserve V; reconcile under the host's freshness contract. Do not downgrade or diagnose rewrite solely from this observation. |
| Proven incomparable tips within the same protocol origin, with sufficient complete evidence | Observable fork/divergent history for this stream identity | Preserve both observations and a blocked condition; stop automatic progress for this stream pending explicit recovery. |
| Missing/incomplete evidence | Unknown | Retain candidates as needed; acquire missing evidence or report incomplete history. Do not turn lack of proof into a negative ancestry conclusion. |

Protocol origin is the origin/binding defined by the selected stream profile, not an arbitrary common Git ancestor pulled in for another purpose. If a profile permits a checkpoint/re-anchor, its explicit transition evidence must be checked; this algorithm does not silently authorize one. A different legitimate stream incarnation is a different S, not an unnoticed replacement under the same identity. Preserving an earlier verified binding does not prove its state is current for a new external action.

A positive ancestry path can be sufficient without reconstructing every unrelated object. A negative ancestry result from a shallow/incomplete graph is not automatically a complete proof. First observation requires the profile's genesis/checkpoint/bootstrap validation; absence of a prior V is not permission to accept arbitrary content.

Validation covers the selected core's format, stream/channel/incarnation bindings, chain rules, identity and required control evidence. Application payload meaning and strong application dependencies can remain uninterpreted/pending. Unknown required authority semantics prevent an unqualified authoritative interpretation; unknown optional application records can be retained opaquely under bounds.

Promote only an exact validated boundary and retain its required closure before recording verified progress. Promotion must be conditional against the prior local verified state, or protected by equivalent serialization, so two ingestion workers cannot regress each other. A moved candidate ref is never itself the evidence. If checking C is expensive, a validated W on the path from V to C can advance; the writer need not become quiet.

A malformed-core entry can block that stream under the chosen validation rule while unrelated streams continue. A locally failed application handler is not a global validity judgment and need not block raw ingestion.

## 5. Route, interpret and advance

1. Enumerate entries from verified retained prefixes according to Q's bootstrap/scan state. Independently processable batches need stable intra-packet coordinates; one OID cannot mean seven of ten records handled unless packet handling is atomic.
2. Compute routing eligibility and Q's delivery identity using its declared scope: per-record coalescing, per-occurrence, per-destination, or another explicit contract. Persist/reconstruct pending selected work before advancing the scan boundary past it. A crash can cause rediscovery; it must not silently lose selected work.
3. Before a particular application action, satisfy that rule's required inputs and predicates: available, structurally valid, authorized under a pinned policy, applied where actually required, and applicable at a stated frontier/purpose. A citation need not have the same obligations as a policy dependency. A recheck does not fence a later external call.
4. Process eligible work with the declared replay/idempotency contract. Persist its outcome/disposition before marking it handled. If local application state and cursor cannot update atomically, use recoverable ordering and safe replay rather than claim atomicity with an unrelated store.
5. Advance the contiguous handled prefix only through entries with recorded qualifying dispositions. Preserve out-of-order completions and pending holes. A nonselected routing disposition does not assert semantic application or global invalidity of that record.
6. Keep scanning/ingestion independent of unresolved application work when required data and pending state are retained. Independent work may proceed around holes if its application permits it. A hot writer or missing dependency must not force repeated rediscovery from zero or block every other stream.
7. Use bounded fair scheduling/backpressure where liveness is claimed. Eventual progress assumes clients run, relevant history remains retrievable, and work receives resources. No bounded latency follows merely from Git availability.

Publication target selection belongs to the writer. Subscription/delivery selection belongs to the reader. Both are needed for T17; neither should be silently treated as the other.

## 6. Dynamic subscription rule: a newly explicit pitfall

Suppose Q originally selects only tests and has scanned through position 100. Change its selector to include design records, leaving the cursor at 100. Design records before 100 were correctly skipped under the old rule but may now be wanted. Reusing the old progress claim without a migration silently loses that history.

Therefore a selector, bootstrap or delivery-scope change must specify prospective-only behavior from a declared boundary, historical backfill, or a new/migrated subscription identity. A stable configuration field is not enough. The same issue occurs when switching from unified record coalescing to per-channel delivery. This is a local subscription contract, not a mandatory global registry or wire field. A migration also states what happens to already pending work; unfollowing is not automatically cancellation of an application obligation.

**T25 — Subscription rule change [dynamic-subscription capability; extension proposed here].** Given Q selecting tests through position 100, change it to include earlier design records, or change record coalescing to per-channel delivery. Expected: explicitly choose a prospective boundary, historical backfill, or a new/migrated subscription identity. Do not silently interpret the old cursor as handling records under the new rule. Preserve or explicitly transfer/dispose pending work according to its actual contract. This adds a named trace without modifying the frozen 24-trace artifact.

Joining/leaving membership, following/unfollowing, channel creation, labeling, and choosing a new subscription version remain distinct operations. A newly appearing stream also requires Q's declared bootstrap/coverage rule; an absent vector element does not mean already consumed.

## 7. Crash cut-points

| Crash after | Recovery obligation |
|---|---|
| Intent exists but E does not | Recover exact intent; prepare according to the selected identity contract. |
| Prepared E exists before a push | Resend/reconcile that same obligation; do not allocate a new intent by accident. |
| Remote acceptance before local evidence | Reconcile target-stream history; keep uncertainty when evidence is insufficient. |
| Some multicast targets accepted | Resume remaining/unknown obligations without claiming atomic all-target publication. |
| Fetch before validation/promotion | Candidate bytes do not advance verified or processing claims. |
| Validated retained data before a progress update | Rediscovery/revalidation is acceptable; required data must still be rooted. |
| Pending work recorded before scan advancement | Redelivery/deduplication is acceptable. |
| Scan advancement before pending work retained | This ordering is forbidden unless pending work is provably reconstructible from retained state. |
| Local application result before handled marker | Replay/reconcile under the local transaction/idempotency contract. |
| External effect before its result record | Use the business operation's provider/idempotency/reconciliation contract; otherwise retain explicit uncertainty and its safe disposition. |

These are ordering obligations, not a mandate to use files, JSON, SQLite, particular ref names, or a separate server. A compaction/retention profile must preserve everything its recovery path depends on, or expose a declared gap/checkpoint boundary.

## 8. Authority remains a profile

For an authoritative noncommutative policy transition, a designated conditional-write history is a reasonable baseline: validate the new transition under the prior policy and reevaluate after conflicts. That does not require every channel to have a global membership state machine. Descriptive labels, independent facts and derived views need not all pass through one policy ref.

Strict policy-versus-data fencing requires an actual host/admission mechanism; a CAS on one ref does not atomically constrain another ref or an external API. The prior local prepared-transaction/proc-receive experiment exercised a narrow guard, not generic hosted enforcement. Retain-all remains the default while retirement/fencing capabilities are unspecified.

External effects and approvals are application contracts. Identical records and deterministic views do not create exclusive effect execution. A sufficient authorized checkpoint or aggregate can legitimately drive a decision; raw-history replay is not universally required.

## 9. Progress claims by stage

For an admissible record selected by Q's bootstrap/scope, eventual verified ingestion depends on eventual discovery, sufficient running/retry opportunities for the reader, reachable authority or another permitted source of the required history, successful local retention, available valid core evidence, and fair service of both streams and entries. The prefix scan must eventually reach that record; fairness among streams alone does not excuse repeatedly selecting only their newest entries.

Routing/delivery additionally depends on the declared delivery scope and a functioning/recoverable queue or equivalent representation. It does not require a model turn or successful application handling. Application progress requires its own eventual-input, supported-rule and termination conditions. External-effect progress has still stronger authority/downstream conditions, and may correctly remain uncertain awaiting reconciliation.

A finite source-retention horizon requires a justified lag/service budget or an explicit history-gap/checkpoint outcome. Fair service provides no universal bound on lag; outages and a growing backlog can exceed a finite horizon. Source data must remain retrievable until the required data/evidence is durably captured, or a declared substitute/gap contract applies. After adequate local retention, later source expiration need not prevent local processing. The retained closure, not merely a source timestamp, determines recoverability.

These are conditional progress statements, not a theorem of bounded latency or a 1000-agent throughput validation. No one generic promise of delivery, processing and effect completion substitutes for the separate stage contracts.

## 10. Questions for peer review

1. Is any state truly redundant given an explicit reconstruction rule? Which crash trace proves the redundancy safe?
2. Does the observation table handle lag, rollback suspicion, incomplete evidence and actual divergence without overclaiming?
3. Does the publish conflict path preserve enough identity to support each candidate codec without a hidden automatic-rebase rule?
4. Does the subscription-change example require an additional trace, or is it already an explicit consequence of Q's versioned scope?
5. What additional assumption is needed to claim eventual delivery under a bounded fair scheduler? Keep it conditional on retention and client execution.

The next refinement should reduce redundant mechanisms while preserving these observable distinctions. No current naming or encoding choice is exempt from a counterexample.
