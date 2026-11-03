# Git-native agent coordination — Joint Decision Record v3

**Status:** reviewed joint recommendation + principles. NOT an implemented, conformant protocol, and NOT a proof of 1000-agent capacity. v3 supersedes v2 (narrow factual corrections from codex's 2026-11-02T205923Z review); v2 and all prior files remain frozen.
**Authors of record:** tpp-claude + git-protocol-codex (independent peers, reconciled adversarially).
**Assembled by:** tpp-claude, 2026-11-03.

**Corrections applied over v2:** (1) removed the "host-invariant per-repo commit ceiling" + vendor push-throughput numbers; (2) qualified the consistency requirement (no universal "Git breaks under eventual consistency"); (3) removed the false "any prunable global converges to channel" claim; (4) qualified identity stability and labelled the ref layout illustrative/unverified.

## How to read

Section A = decision + implementable detail. B = decisions/reasons/intent. **C = roads not taken** (every alternative, with pros/cons/when-it-wins/how-to-revive, so any can be picked up later). D = open human choices. E = evidence + pointers. F = implementation starting points.
Tags: **AGREED / CONTESTED / HUMAN / UNTESTED.**

---

# A. THE DECISION

## A.0 TL;DR

For a **single repository used purely as a communication bus** (not a code repo) serving **~1000 globally-distributed agents for 24h+**, with **ephemeral rooms (2–30 min), DMs, broadcast, and hierarchical task/sub-team/report dynamics**, both agents independently recommend:

> **Topic-scoped producer logs** — per-(room, writer) append-only streams in the one repo, with independent per-subscription cursors. (The "channel streams" family, named precisely.)

Justification is **architectural fit** — the conversation boundary (a room) is also the natural boundary for discovery, reading, lifecycle, and failure isolation — **not** an immediate-garbage-collection win (that claim was examined and retracted; see C.1/C.6).

## A.1 Context and hard constraints

- **One repo.** All agents collaborate in one shared repository. Repo-level sharding is out of scope (C.5).
- **Communication bus, not code.** Holds the protocol/spec, utilities, and the message log. Separate code repos exist elsewhere.
- **~1000 agents, globally distributed**, ~100 co-located on one system; 24h+ continuous.
- **Dynamic rooms** (2–30 min), hundreds per room then regroup; DMs; broadcast; recursive task→sub-team→parent-report; persistent test/lint/CI roles across many rooms.
- **Host-consumer:** we consume an existing Git host; we don't build it. The Cursor "Git at any scale" article informed our understanding of host bottlenecks (packfiles, DAG walks, publication serialization on some backends, compaction) but is background, not a blueprint and not a source of portable numeric bounds.

## A.2 Chosen design — topic-scoped producer logs (implementable detail)

**Ref layout — ILLUSTRATIVE, host-mapping UNVERIFIED.** The paths below are a conceptual namespace. Generic hosted support for arbitrary `refs/gc/...` is not established; a **branch-backed mapping may be required** on some hosts. The eventual spec must state which namespaces are remote vs local-only and the push allowlist explicitly. **Control refs must not collide with a parent prefix used by writer refs.**
```
<data>/room/<room-id>/<writer-id>      — per-(room, writer) append-only stream (data plane)
<data>/dm/<dm-id>/<writer-id>          — DM: a logical alias of the room primitive (2 participants)
<data>/broadcast/<writer-id>           — broadcast: a logical alias; one well-known room
<data>/role/<role>/req/<writer-id>     — role-request channel (logical alias) for service agents
<meta>/...                             — protocol/spec/utilities, kept OFF the data-stream ancestry
<local>/cursor/<sub-id>/...            — LOCAL per-subscription cursors (never pushed)
<local>/verified/<sub-id>/...          — LOCAL durable verified-observation refs (never pushed)
```
DM / broadcast / role are **logical aliases/applications of the same channel primitive — NOT four different core parsers.** Room IDs are unique/immutable with a human label + optional parent/task metadata; **hierarchy is metadata only**, no Git branch inheritance or authority.

**Publish:** a writer appends a commit to its own room/writer stream and pushes. Single-writer-per-ref → no writer-vs-writer contention. Multiple messages/rooms can coalesce into **one network push** (A.6).

**Subscribe/read:** fetch the rooms of interest by **scoped ref-prefix fetch where the host honors it, with correct client-side filtering as the fallback** (not an assumption the server honors `ref-prefix`). Fetch into **candidate** → validate → promote to a **durable verified** observation → advance an **independent per-subscription cursor**. A room has a *vector* of per-writer positions, not one room-wide offset.

**Delivery:** **independent subscribed-reader fan-out under each subscription's declared bootstrap / filter / retention / execution assumptions.** Enrollment is NOT subscription; Git storage does not itself schedule or guarantee delivery to every agent.

**Record identity / envelope — CONTESTED, two viable OPTIONS (pick ONE at interop-cut, D.3):**
- *Rich/general:* record = Git tree `R(metadata+body+artifacts)`; commit wraps `R`; **record identity = R's tree OID**; occurrence = commit OID + position; delivery = subscription key. **Only an unchanged R is stable under a different publication wrapper** (that is the repackaging property). Adds tree+blob objects per message.
- *Compact/text:* routing in trailers, body in the commit; identity = commit OID — **stable only while that exact commit is preserved; rebuilding the commit changes it.**
Neither fingerprint recovers erased intent: **intentional duplicates need a nonce in metadata; retries need a journal/durable caller identity.** Options, not two mandatory parsers; **independent of topology.**

**Discovery:** independently-written room refs **are** the discovery substrate (scoped prefix fetch); known-room invitations can carry the locator directly. A live-room **index is rebuildable ergonomics only — never a global registry branch mutated on every message** (write hotspot).

**Evidence promotion (hierarchical tasks):** a parent pins selected child **record-trees** as real tree entries, citing the rest semantically — preserving findings without making the child's whole ancestry its Git parent. A retention convention, not auto-discard permission.

**Local-ingress optimization (the ~100 co-located agents):** one host fetches once and fans out to many local subscriptions, and may transport several writers' already-prepared refs in one push **without authoring their records**. Ownership/locking/journals explicit. Optional; not a coordinator or mandatory service.

## A.3 Retention — retain-all default; close/archive/expire SEPARATE

Default **retain-all** until a different contract is chosen. Stages are distinct: (1) room stops accepting work, (2) late publication fenced/reconciled, (3) history available to lagging readers under policy, (4) selected results retained for parents, (5) stream refs retired when safe, (6) data unreachable from all roots, (7) host removes eligible objects under ITS policy.

**Four separate metrics:** logical fetchability, active ref count, reachable object bytes, physical hosted storage. **Client ref deletion ≠ immediate physical reclamation** — the host controls GC; we cannot promise a server GC deadline on an unspecified host.

**Late-writer fencing (UNTESTED):** deleting a closed room's refs is **insufficient** — a paused writer can recreate a deleted ref (deletion erases the expected-value boundary). Bounded retirement needs a finalization authority + stream catalog + late-writer recovery + protected roots + gap rules; the receiver-owned policy-transaction we tested addresses one admission race but **may not exist on an arbitrary host**. Early deployments **retain all** while measuring; retire only under a defined profile.

## A.4 Consistency profile (deployment assumption) — HUMAN / UNTESTED

State the selected profile explicitly rather than assert a universal failure. Requirement: **a coherent authoritative conditional-write history per stream; do NOT treat independent writable mirrors as one authority.** A simple first profile may assume **monotonic / read-your-writes access from one authoritative endpoint.** A lag-aware reader preserves its verified tip and retries authoritative reconciliation; **a stale read must NOT be taken as proof of publication failure or rewrite.** No global atomic snapshot or cross-stream total order is required merely because the host is shared. Mark host verification UNTESTED.

## A.5 Inherited correctness fixes (from v1, AGREED)

A1–A6 (v0.4) and R1–R8 (v0.5) carry forward: tri-state ancestry (refuse only shallow/incomplete-commit proofs; a blobless clone with complete DAG is fine), durable candidate→verified rewrite halt, uniform cursor namespace + dedicated lock over read→handle→advance, `last_scanned` advance (never past a failed addressed record), chain/identity validation via the shared validator, extensibility via fixed critical set + version bump. Full table in v1 §2.

## A.6 Write cost — shared host resources; workload-dependent; NOT topology-neutral

Both layouts share the selected host's finite CPU/I/O/network/durability resources. **Some backends impose a repository-level publication bottleneck; its presence and capacity are deployment/workload facts to be measured on the chosen host — not a portable constant, and not the vendor push-throughput figures from the article.** Linearizability does not require repository-global exclusive execution.

Batching reduces fixed overhead for both, but **does not equalize write cost**: e.g. 100 unicast messages to 100 rooms in one batch = **1 global head update** (global) vs **100 channel head updates** (channel). Channel carries higher ref/wrapper/lifecycle write cost; this is a real, workload-dependent cost of the chosen design. Plan batching + backpressure regardless; derive any actual bound from measurement.

---

# B. WHY (decisions, reasons, intent)

| # | Decision | Choice | Why / Intent |
|---|----------|--------|--------------|
| B1 | Topology | Topic-scoped producer logs (per-room/writer) | Conversation boundary = discovery/read/lifecycle/failure boundary. Fits selective rooms, persistent roles, WAN read isolation, skew. |
| B2 | Partition key | By topic (room), sub-by writer | Consuming a room must not drag unrelated producer traffic. |
| B3 | Writer model | Single-writer-per-ref | No writer contention; linear per-writer order free. |
| B4 | Record identity | Record-tree OID (rich) OR commit OID (text) | Content-addressed; unchanged-R stable under re-wrapping; commit OID stable only if the exact commit is preserved; nonce+journal for intent. Decoupled from topology. |
| B5 | Retention | Retain-all default; close/archive/expire separate | Short room life ≠ discard; a dead sub-team's report may be the valuable part. |
| B6 | Discovery | Room refs are the substrate + rebuildable index | Avoid a global registry write hotspot. |
| B7 | Service agents | Role-request channels | Persistent roles read typed requests, not every room. |
| B8 | Hierarchy | Metadata only; evidence promotion via record-trees | Keep findings without inheriting child ancestry; no Git-authority implication. |
| B9 | Co-located agents | Optional local-ingress fan-out | Fetch once, serve many local subs; one push for several prepared refs. |
| B10 | Write scale | Batching + backpressure; measure the host | Real ceiling is deployment-measured, not a portable constant; channel's ref write cost is higher (A.6). |

**Overall intent:** choose the boundary that makes the common dynamics (ephemeral selective rooms + persistent roles + hierarchical reporting) cheap to reason about and operate, accepting higher ref-write cost and a retirement-discipline burden as the price. We did NOT optimize for the multicast-heavy / fully-overlapping-readers case, which favors global (C.1).

---

# C. ROADS NOT TAKEN (preserved for revival)

## C.1 Global producer outboxes (partition-by-producer) — main alternative
**Design:** one outbox per agent; a room is virtual (commits tagged with destinations); multicast = one commit, K tags, **one head update**.
**Pros:** cheapest multicast; **fewest ref mutations and retained stream identities** (≈ N writer heads, independent of room churn — avoids channel's 48k–720k refs/day); simplest provenance; **simpler continuity as agents move between rooms**; **economical shared local ingestion** for broadly-overlapping readers.
**Cons:** selective reader fetches a producer's all-room ancestry → WAN read amplification, worst for hot persistent agents; a malformed core packet blocks that writer across its channels; **an unchanged, append-forever, mixed-ancestry outbox cannot selectively expire its interior records** (per-room expiry needs coarse time-epoch rotation, C.6, or a snapshot/checkpoint profile).
**Not a namespace-only swap:** routing/demultiplexing, the discovery catalog, and retention rules all change; total refs = ≈ N writer heads **plus** room descriptors/catalogs and any archive/index roots.
**When it wins:** highly-overlapping readers, frequent true multicast, low room churn, low ref-churn tolerance, retain-all or coarse-time retention.
**How to revive:** per-agent outbox namespace; client-side room demux on destination tags; adopt C.6 (time-epoch) or a producer-snapshot profile for bounded retention; reuse cursors/validator/identity/batching unchanged.
**Correction vs v2:** the earlier "any attempt to prune rooms converges to channel" was wrong and is removed. A producer snapshot/checkpoint profile can retain selected logical records and retire old producer epochs **without per-room refs** (more complex: identity/gap/rebuild costs). The narrow true statement is only: an *unchanged append-forever mixed ancestry* cannot selectively expire interior records.

## C.2 Shared room append/CAS — declined as data plane; keep for serialized control
One ref per room, all writers CAS. Pros: easy discovery, room-wide total order, one ref/room. Cons: writers serialize on CAS → contention under fast publishers; no fairness. **Keep for** membership policy, task awards, decisions, deliberately-serialized low-volume channels. Revive when a channel needs one authoritative total order at low write rate.

## C.3 Immutable per-packet refs — declined pending bounded-ref-lifecycle evidence
Each message is its own ref/root. Pros: fully independent publication; removing one root doesn't cut unrelated ancestry. Cons: O(packet) refs, inventory churn, explicit ordering/gap semantics, expiry races. Revive for bounded ephemeral exchanges or if measurements show packet-granularity ref lifecycle is acceptable on the host.

## C.4 Adopt a collaborative entity format (git-bug / Radicle) — deferred, adapter path kept
Reuse a mature Git-native collaborative-object model. Pros: proven data model, offline concurrent edits, deterministic merge. Cons: doesn't specify our subscription/expiry/award behavior; adopting a runtime changes the deployment target; borrowing the format needs a precise compatibility promise. Revive when durable collaborative-object semantics become primary or the team already runs those clients. Refs: git-bug data model `https://github.com/git-bug/git-bug/blob/trunk/doc/design/data-model.md`; Radicle `https://radicle.dev/guides/protocol`.

## C.5 Repo-per-room / repo sharding — OUT of scope (one-repo constraint); documented
**Design:** each room its own repo; the host makes repos the scaling/replication/GC unit. **Pros (conditional):** shards write/compaction load; per-room retention = delete a repo; zero cross-room read amplification. **Cons:** violates the one-repo constraint; cross-room multicast spans repos (K non-atomic pushes); needs a cross-repo registry; **cannot split one hot 1000-writer room**; can explode DM-repo provisioning; loses one-push multi-ref and shared-object dedup; **host resource isolation is only conditional, not guaranteed**; known-room locators need no universal registry; physical deletion still host-dependent. **Revive when:** the one-repo constraint is lifted AND repos are genuinely cheap on the host — preferably as a bounded pool of pre-existing shard repos + hot-room isolation, not naive repo-per-room.

## C.6 Global time-epoch rotation — reclamation technique for C.1 (kept)
Start independent producer epochs periodically; retire whole old time-buckets under a lifecycle policy. Bounds retained history **coarsely and uniformly** (by time) with grace + explicit gaps. Cannot expire one room independently while keeping other records in the same bucket unless separately retained. This is the retention mechanism the global design would use, and a legitimate coarse option where per-room precision isn't needed.

---

# D. OPEN DECISIONS DEFERRED TO THE HUMAN

1. **Retention profile — HUMAN.** Retain-all vs bounded-history; what survives after close; which results survive longest. Default: retain-all while measuring.
2. **Host admission/fencing — HUMAN/UNTESTED.** What fencing/finalization operation actually exists on the chosen host? Don't build retirement around an uninstalled hook.
3. **The one interop cut — CONTESTED.** Rich record-tree vs compact text-commit as the first conformant parser. Both viable; one is selected, not two mandatory parsers.
4. **Budgets — HUMAN/UNTESTED.** Real publication latency, message rate/size, subscription overlap, polling budgets. Agent count + room lifetime are insufficient to size.
5. **Consistency profile — HUMAN (gate).** Confirm a coherent authoritative conditional-write history per stream from one authoritative endpoint (not independent writable mirrors). Mark host verification untested.

---

# E. EVIDENCE AND POINTERS

## E.1 Experiments (local, scope-limited; not throughput/WAN benchmarks)
- v0.4 read-race: hot-writer equality gate starves a controlled schedule (→A1).
- v0.5 countertraces: restart loses overwritten observation (→R2 durable verified-tip); cursor D/F ref conflict (→R3); shallow ancestry false-negative (→R1 tri-state).
- Matched layout accounting (6 writers/4 rooms/120 records): room0 cold **local** pack 528,056 B (global) vs 158,865 B (channel, ~30%); 84 vs 0 unrelated publications; channel +2.7% source bytes, 4× refs. Local pack bytes, not WAN.
- Ref-advertisement study (10,100 refs): naive per-writer `ls-remote` advertised all 10,100 (~796 KB); scoped v2 wildcard FETCH advertised 100 (~7.9 KB). → scoped fetch where honored, filtering fallback otherwise.
- Policy-ref + proc-receive: one admission race fenced locally; multi-ref atomicity/auth/archive/crash/host-compat UNTESTED.
- Channel churn arithmetic: N·T/L ⇒ ~48,000 (L=30min) to ~720,000 (L=2min) writer-refs/day unretired; bounded by c·a·(L+grace) with a retirement protocol. Room descriptors/archive roots still grow; archiving writer-heads into one root cuts active refs but not payload bytes and can reintroduce fetch amplification.

## E.2 Source artifacts (this session's `attachments/`, prior files FROZEN)
Specs: `gitcomms-spec-v0.4.md` (prior session), `gitcomms-spec-v0.5-draft.md`.
Records: `git-coordination-decision-record-v1.md`, `-v2.md` (frozen), this `-v3.md`; contributions + cross-reviews v1; codex analyses (`codex-concrete-mechanisms-v1`, `codex-cursor-git-scale-analysis-v1`, `codex-host-consumer-sharding-analysis-v1`, `codex-ref-discovery-findings-v1`, `codex-record-tree-identity-option-v1`, `codex-one-repo-dynamic-workload-verdict-v1`, `codex-decision-record-v2-review-v1`) + their `.py`/`.results.json`.
Ledgers: tpp `/Users/I533118/personal/code/claude_agent-coordination-research/research-ledger.md`; codex `/Users/I533118/personal/code/agent-coordination-research/`.

## E.3 Status honesty
Converged on a recommendation + principles. NOT an implemented conformant protocol; NOT a proven 1000-agent capacity. Open human choices are steering options, not approval blockers. All conclusions remain open to challenge.

---

# F. IMPLEMENTATION STARTING POINTS

1. Pin the interop cut (D.3); write the one shared validator (A.5) for it.
2. Build client utilities: publish (append+batch push), subscribe (scoped prefix fetch → candidate → verified → cursor advance), local-ingress fan-out (A.2).
3. Implement room lifecycle as separate close/archive/expire (A.3); start retain-all; add retirement only behind a defined fencing profile (D.2).
4. Stand up role-request channels (B7) and the broadcast room (A.2).
5. Verify the consistency profile (A.4) and measure real budgets (D.4) on the actual host with a text-heavy high-churn fixture before any scale claim.
