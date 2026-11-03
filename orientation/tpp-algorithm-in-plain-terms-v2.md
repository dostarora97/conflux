# The algorithm, in plain terms — v2 (honest-at-altitude)

An orientation layer for the git-native agent-coordination protocol. It POINTS at the precise contracts and must not assert more than they do. v1 is withdrawn/frozen; this v2 incorporates codex's ten corrections (codex-plain-terms-review-v1.md). Authoritative artifacts: decision-record v3, semantic-trace-suite v2 (24 traces), algorithm-review v2 (+T25), optional-attention-harness-note v2. Status: a converged recommendation + precise algorithm, NOT an implemented protocol or a proven 1000-agent capacity.

---

## The shape

Each writer appends to **its own stream** within a **channel**. Ordinary publishers therefore do not compete to append to one shared conversation log. The host guards stream updates, and readers retain and check the history they observe. An application needing authoritative shared policy declares a **separate authority profile**.

A channel is the shared primitive behind a room, a direct exchange, a broadcast, and a service-request queue — but these differ in bootstrap, delivery, admission, and retention **policy**, not merely in membership count. Application authority is **optional**, used when its invariants require it; short channel lifetime does not prove a channel is policy-free. The underlying publication authority and the core identity/interpretation bindings stay explicit.

## Publishing

- **Retain first.** Keep the submission identity and the exact prepared inputs before any network attempt, under a declared local persistence contract. Reuse them on retry so recovery does not accidentally invent a new intent. (A nonce is one mechanism for distinguishing intentional duplicates, not a required universal field.)
- **Append and request** the conditional update at the stream's authority.
- **On an unclear outcome, look — don't guess.** Look for the exact prepared occurrence, or an explicitly equivalent intent, in the **target stream's accepted history**; it may sit beneath a later tip. A stale or incomplete observation leaves **uncertainty** — which is carried honestly, not resolved by assumption. Equal prose, a locally-present object, or a record elsewhere in the channel is not proof the target publication succeeded.
- One message to K channels is **K obligations**, reconciled independently; no default cross-target atomicity.

## Reading

- **Fetch the channels you care about** (scoped where the host honors it, with correct client-side filtering otherwise).
- **Scratch, check, then trust.** Fetch each candidate, **pin its exact fetched version**, and classify against what you last verified — and ancestry alone validates nothing; the stated format, identity, and core-evidence checks still apply:
  - clean graph extension (+ passes checks) → promote a verified prefix;
  - an **older** candidate → **lag or a possible regression** (not definitely lag) → keep the verified boundary, reconcile under the host's freshness contract;
  - genuinely divergent with complete evidence → stop and flag;
  - a **different protocol origin claiming the same stream** → a **competing identity claim** (not an "impostor" — motive and authorship aren't established): quarantine it against a prior verified binding when one exists; without a trusted prior binding, there is no automatically-trusted original; an authorized re-anchor needs its own transition evidence;
  - insufficient evidence → **unknown**; conclude nothing.
- **Track the exact stream entry/boundary** (including a position inside a batch when the profile requires one). **Timestamps are metadata, not progress cursors.**
- **Advance by stage.** A scan/ingestion cursor can advance before application handling *when the required data and pending work are durably retained or reconstructible*. A handling cursor advances only through qualifying handled dispositions. Remember out-of-order completions and unresolved holes; a retryable failure can remain owed work. (An unqualified "advance only after handled" would recreate the head-of-line blocking this design avoids.)

## State changes (only where a channel declares an authority profile)

Authoritative, order-sensitive policy changes go through a designated **conditional-write authority**, reevaluated on conflict — not a multi-writer merge. Descriptive labels, independent facts, and derived read-only views need not pass through that authority, and such views may legitimately differ between readers. Strict policy-versus-data fencing requires an actual host mechanism; a conditional write on one ref does not atomically constrain another ref or an external API.

## The honest edges

- **External effects:** the core does not itself guarantee exactly-once arbitrary external effects. A specific provider/application may supply a stronger business-effect guarantee under its own contract. A business key, idempotency, authority, fencing, and reconciliation are mechanisms chosen for the actual invariant — not a universal requirement for every application.
- **Liveness is staged and bounded by assumptions, never a deadline.** Eventual ingestion depends on discovery, sufficient reader/retry execution, retrievable valid core evidence, successful retention, and fair service that actually reaches the record. Routing and application processing add their own conditions; application completion can require eventually-available inputs and terminating work; uncertain external effects may correctly wait for reconciliation. A finite source-retention horizon needs a justified lag/service budget or an explicit gap/checkpoint outcome; fairness supplies no finite lag bound; after adequate local capture, source expiry need not prevent local processing. Git availability alone supplies neither eventual application success nor a deadline.
- **Changing a subscription is not free.** Widening a selector or switching delivery scope can make previously-excluded history now-wanted; reusing the old cursor silently loses it. A scope change needs a prospective boundary, backfill, or a new/migrated subscription identity. (→ T25.)
- **Deleting a ref is not erasure.** Logical closure, hiding, ref removal, and physical reclamation are four separate things; the host controls the last.

## Why this shape (workload-scoped, not a universal proof)

Channel-scoped single-writer streams fit the stated selective-room / persistent-role / hierarchical-reporting workload, because the conversation boundary is also the boundary for discovery, reading, lifecycle, and failure isolation. It is a **recommendation with real costs** (more refs/wrappers, a retirement obligation), not a proof that channel is the uniquely correct boundary. The retained global-outbox alternative wins for other overlap/multicast/ref-budget patterns (decision-record §C.1).

---

## Navigation map (which question → which precise contract)

- "How exactly is a conflicting fetch classified?" → algorithm-review v2 §4 (observation table) + §1 (T03 claims).
- "What survives a crash, and in what order must I persist?" → algorithm-review v2 §7 (crash cut-points).
- "What does publish do on an unknown push outcome?" → algorithm-review v2 §3 + trace T15.
- "How do multicast and delivery scope interact?" → trace T17 + algorithm-review v2 §5.
- "What happens when I change what I subscribe to?" → algorithm-review v2 §6 + trace T25.
- "Which topology, and why not the other?" → decision-record v3 §A/§B and §C.1 (global alternative, preserved).
- "How does a model avoid being woken on every message?" → optional-attention-harness-note v2.
- "What did prior art teach us to avoid?" → codex-prior-art-and-semantic-distinctions-v1 + the previous session's matrix-git-swarm-research.md.
