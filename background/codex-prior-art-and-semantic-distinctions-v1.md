# Prior-art lessons and semantic distinctions — Codex v1

2026-11-02 UTC. Independent peer-review proposal, not a joint specification. All previous artifacts remain unchanged. The human has reopened fundamentals; the current architecture recommendation is a hypothesis we can revise. Primary web sources below were checked during this audit. Mutable online specifications are research snapshots, not pinned conformance targets.

## 1. Minimality means preserving observable distinctions

A small protocol should have few mandatory mechanisms, not few words at any cost. Two cases can share a representation only when the protocol does not need to distinguish their permitted outcomes. If two histories encode identically but require different recovery, authority or application behavior, the encoding has lost information. This is a practical test, not a claim to have proved a globally minimal ontology.

Start with entities, relations and permitted observations; choose names afterward. Keep the small required model separate from the vocabulary needed to explain optional profiles. Ten precisely defined concepts do not imply ten mandatory fields on every record.

Promising core family: **record, stream, channel**. Supporting concepts when needed: **reference, position, frontier, subscription, cursor, view**. A publication **entry** distinguishes an occurrence from its content if the chosen representation permits batching, forwarding or multicast. This conceptual distinction need not impose an extra object in a codec where occurrence and record are deliberately one-to-one.

## 2. Prior-art lessons: retain the failure, not the whole machinery

Each paragraph distinguishes documented behavior from our proposed adaptation. These are design lessons, not audits of those implementations.

**Matrix: identity and authorization resolution are separate problems.** Project Hydra describes a state-reset defect and a distinct creation-event uniqueness defect, addressed through state-resolution changes and room IDs derived from creation events. Its stated affected deployment is federation with untrusted servers; private trusted federation is outside that issue's scope. Our inference: authoritative conditional policy transitions can avoid the federated competing-authorization-resolution problem, but genesis identity, dependency closure and admission enforcement still need definitions. Do not claim that avoiding a merge deletes every associated failure mode. [Project Hydra](https://matrix.org/blog/2025/08/project-hydra-improving-state-res/)

**XMPP: durable affiliation is not temporary role, and role is not liveness.** XEP-0045 distinguishes affiliation across visits from privileges during a visit. Our inference: enrollment, permission, subscription and observed presence must not be one joined flag. We should not translate XMPP role directly into presence: a temporary privilege is different from an observation that a process recently communicated. Preserve the separation without importing owner/admin/visitor classes. [XEP-0045 terminology and roles](https://xmpp.org/extensions/xep-0045.html#terms)

**SSB: one author identity can become an accidental write bottleneck.** The original paper explicitly describes competing chains when two devices concurrently publish under one identity, recommends distinct device keys, and discusses partial-order consequences. It also identifies whole-chain verification as a partial-replication cost. Our inference: logical agent identity must be separable from independently active writer incarnations; cloned state after restart is a normal failure case. Per-channel streams trade additional identities for selective synchronization; do not assume the global-feed model gives selective history for free. [SSB paper, §§6.1 and 6.3](https://conferences.sigcomm.org/acm-icn/2019/proceedings/icn19-19.pdf)

**Yjs: a user ID is not a concurrency identifier.** Its FAQ warns that simultaneous document instances sharing a ClientID can corrupt the document, and recommends session-specific ClientIDs while identifying users separately. Our inference: stable agent labels must not be reused as an implicit exclusive-writer token. Either fence multiple processes sharing one stream or allocate distinct stream incarnations and preserve their history. We need not adopt Yjs or a per-process key hierarchy. [Yjs FAQ](https://docs.yjs.dev/api/faq)

**Nostr: event identity, addressable state and query boundaries differ.** NIP-01 defines exact serialization for event hashes, distinct replaceable/addressable conventions, timestamp-based filtering, and an end-of-stored-events marker. Our inference: hash inputs define identity; identical serialized intents collapse unless distinguished. A bounded query ending does not certify all relevant records exist or that a timestamp is a reliable recovery cursor. Mutable-address lookup and immutable-record lookup must be named separately. [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md)

**Nostr deletion: a request is not erasure.** NIP-09 separates deletion requests, relay behavior and client presentation, and explicitly says deletion cannot be guaranteed everywhere. Our inference: disown, hide, stop serving, remove roots and physically reclaim need separate contracts. Our private-team setting does not need public-network machinery to benefit from this distinction. [NIP-09](https://github.com/nostr-protocol/nips/blob/master/09.md)

**git-bug: operation packs and reducers are useful; their domain rules are choices.** Its generic DAG format batches operations, retains attachments through actual tree entries, defines deterministic clock-based replay and preserves unknown operations while excluding them from snapshots. Our inference: batching must preserve record coordinates; content references need retention roots; opaque preservation does not mean authoritative understanding. Its clock discussion must not be read as saying unequal clocks prove causality. Its merge description also does not establish that continuously concurrent mergers must reach one physical commit tip. [DAG entity specification, §§6–10](https://github.com/git-bug/spec/blob/trunk/dag-entity.md)

**Radicle: replicated history and materialized interpretation are separate.** Its guide describes per-peer namespaces over a shared object database, identity rooted in an initial document, and COB histories reduced with defined ordering and conflict behavior. Our inference: retain independent history without silently choosing a semantic winner. Stable initial identity can coexist with evolving metadata. Reusing these lessons does not require the Radicle network or its authority scheme; logical view convergence does not require identical merge-commit topology. [Radicle protocol guide](https://radicle.dev/guides/protocol)

**Lamport: an ordering extension is not causality evidence.** Happened-before implies increasing logical time; the converse does not hold. Our inference: display order and deterministic tie-breaking must never be evidence of reading, agreement, precedence of policy admission or exclusive ownership. Even a correct causal ordering reflects the system events and dependencies actually modeled. [Time, Clocks, and the Ordering of Events](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)

**Our local failures are prior art too.** Requiring an inventory tip to equal a later fetch tip can starve a hot writer; process a verified fetched prefix instead. Mutable remote-tracking refs can erase evidence across restart; retain verified observations separately. A shallow graph can invalidate a negative ancestry conclusion. Git ref path prefixes can create directory/file collisions. A JSON hash string does not retain its object. These were local mechanism experiments, not production-scale benchmarks. The shared artifact index identifies the immutable experiment scripts and results.

The historical web-research synthesis and follow-up also contain useful cancellation, effect-idempotency and notification-reconciliation reasoning. Their mandatory registry, signature, task-state and causes proposals are historical options, not requirements carried into the generic core. I have fully read both and the historical Matrix research for this audit; I have not newly audited every historical implementation.

## 3. A compact model, independent of codec

Let R be immutable records, E publication entries, S stream identities and C channel identities. There are functions content:E→R and stream:E→S. Entries in a well-formed stream have a defined append order. In the channel-scoped layout, channel:S→C binds a stream to a channel. That binding is a layout choice: a global-outbox profile could instead associate channel destinations with entries.

A stream identity must distinguish independent incarnations where concurrent writers are possible. A writer can be a logical principal with several serialized processes, or a particular producer incarnation; the profile must choose rather than assume a human-readable agent name gives exclusivity.

Record identity, publication-entry identity, local delivery identity and business-effect identity are different domains. A codec may intentionally equate two domains, but must state the consequences. A repeated request with the same words can be a new intent; republishing the same record can be a new delivery occurrence without being a new business intent.

No requirement here forces JSON, signatures, universal UUIDs, a particular schema library or a third-party runtime. The open native-commit versus immutable-record-tree choice must settle which identity domains exist in the mandatory profile and which mappings are lossless.

## 4. Four different relations must stay different

1. **Git reachability** determines object transfer and retention under Git rules.
2. **Stream order** orders publication entries within a stream.
3. **Typed references** express reply, citation, supersession, grouping, or semantic dependency.
4. **Execution happened-before** concerns observations and actions of actual processes.

Some edges can serve more than one purpose if explicitly specified. None of these relations should be silently treated as all the others. Git parentage added only to retain an archive is not proof that the writer read or endorsed every ancestor. A reply or citation need not be a processing prerequisite. Arbitrary references can be cyclic; a causal-dependency relation cannot be.

For a strong dependency, semantic application may require a verified dependency closure. For a citation, a missing target can remain an intelligible unresolved reference. Raw ingestion should not be blocked globally because one application cannot yet interpret one record. Conversely, do not apply a policy transition whose required authorization history is missing merely because raw ingestion succeeded.

## 5. Position, cursor and frontier

A **position** locates a boundary or entry in one stream under a defined coordinate scheme. An OID is enough only if the profile defines one processing unit per commit or commits are processed atomically. If a commit batches ten independently processed records, a resumable coordinate may need the commit plus record ordinal or an equivalent stable identifier. A commit OID alone cannot mean seven of those ten records were processed.

A **cursor** is durable reader state asserting progress for a named subscription, stage and rule. Its value can be a position or a vector. Ingested through X and applied through X are different claims. Out-of-order application requires holes, a pending set or a contiguous-prefix cursor; taking the highest processed coordinate loses gaps.

A **frontier** is a boundary over a specified stream universe and order. For independent stream prefixes F:S⇀Pos, define H(F) as the union of each included prefix. Missing stream entries mean unspecified coverage unless a catalog/discovery contract explicitly says otherwise. Include stream incarnations, scope/catalog version where needed, and the claimed stage. A finite vector need not assert that it lists every stream that exists.

Counterexample: A has a1<a2; B publishes b2 depending on a2. F(A)=a1, F(B)=b2 gives valid per-stream prefixes but not a down-closed cut of the dependency graph. It is down-closed for the disjoint per-stream order. Therefore prefix frontier and causally closed frontier are not synonyms. We do not need globally atomic discovery to report an honest partial frontier.

A **view** is an interpretation of selected history under rules: V=P(H(F), selector, rule-version, context). Equal complete inputs and deterministic rules imply equal outputs. They do not imply global completeness, factual truth, human agreement or irreversible finality. A digest's input frontier bounds what it could summarize, not what the digest faithfully included.

## 6. State, authority and convergence

Avoiding Matrix-style federated authorization resolution is a reasonable baseline preference: change authoritative policy through a conditional update at a designated authority, reevaluating preconditions after conflict. This sacrifices authoritative offline policy updates during a partition. It does not prohibit convergent read-only views, independently retained facts, or future explicitly specified mergeable application data.

Serialization alone is insufficient to prove transition validity: a successfully appended unauthorized operation remains invalid under the policy. Nor does CAS on the policy ref atomically check that policy during a separate data-ref update. Generic hosted Git may lack the cross-ref admission mechanism required for strict fencing. Our local prepared-transaction/proc-receive experiment tested a narrow guard; it was not a complete hosted authorization, multi-ref, archive or crash implementation.

Convergence needs a named object: record sets, per-stream accepted prefixes, derived views, authority decisions and physical Git tips are different targets. Under quiescence and eventual synchronization, clients can converge on retained records without agreeing on a scientific conclusion. Deterministic ordering can display disagreements consistently while preserving them.

## 7. Roles, lifecycle and stage claims

Do not collapse **author**, **stream writer**, **publisher/forwarder**, **transport helper**, **reader**, and **subscriber**. We should choose an exact meaning for publisher before making it a field name: it might mean the logical publication principal or the actor performing a remote push. A host-local helper can transport prepared records without authoring them; a parent can promote a child's immutable finding into a broader channel. Provenance and the transport credential are separate facts.

Useful stage vocabulary: prepared, published, ingested, routed/delivered, presented, applied, effect outcome. These are scoped observations, not one mandatory pipeline. A record may need no effect; deterministic code can act without a model turn. Presented means made available to a specified consumer, not understood. Publication means the designated authority accepted the ref update under the host's contract, not permanent storage everywhere. A timeout after pushing is an unknown outcome, not proof of rejection.

Lifecycle is a product of axes, not one open→sealed→archived→expired enum:

| Axis | Examples | Does not imply |
|---|---|---|
| Publication admission | open / closed to new publication | history removed |
| Local interest | follow / unfollow | membership revoked |
| Enrollment | registered / departed / removed under policy | current process online |
| Permission | allowed / denied for an action | old copies erased |
| Presentation | visible / hidden / redacted view | bytes reclaimed |
| Retention | retained / eligible for reclamation | host GC has run |
| Physical storage | known present / confirmed reclaimed / unknown | all replicas agree |
| Application work | pending / resolved under a rule | every cited request answered |

An archive is a retained history arrangement. Expiration requires an explicit scope and policy. Deleting an active ref neither proves erasure nor prevents a stale writer recreating it. A new channel reusing an old label needs a distinct identity or an explicit continuation contract. Removal terminality is a policy choice requiring a re-enrollment/incarnation rule.

## 8. Vocabulary choices still open

**Channel** is a good generic routing/context noun. It does not imply Slack semantics, an ACL boundary or two-person confidentiality. DM, broadcast and role-request are uses with potentially different membership/admission/retention policies, not merely cardinality. A thread is a relation within or across such contexts, not automatically another channel.

**Record** is suitably neutral. Event, command, request, measurement and message can remain application types. An event record is still an authored claim unless an observation/evidence rule establishes more.

**Descriptor** is reasonable for descriptive metadata; **policy** is clearer for authority-bearing rules. These can share a versioned document without equating their meanings. Manifest does not inherently mean static, so replacing it is a readability preference. Do not rename every occurrence merely to maintain a metaphor.

**Outbox** remains a useful name for a local durable publication queue or for the global-outbox alternative; it is not the canonical noun for the chosen channel-scoped remote stream. Familiar words are useful at the right layer.

**Frontier** can be the precise specification term while a CLI says progress or covered through. **Snapshot** names serialized state, **checkpoint** a recovery contract, and **index** a lookup structure. A snapshot is disposable only if all inputs and rules needed to rebuild it remain available; after compaction it may become essential. We need not make all three mandatory artifacts.

## 9. Semantic conformance traces to carry forward

These are proposed observable test histories, not claims that a complete implementation exists:

1. Two identical texts represent distinct intents; retrying one intent retains its identity.
2. One immutable finding is forwarded into two channels; authorship survives and subscription delivery remains scoped.
3. Two clones resume one writer identity; a divergence is preserved and reported, not silently merged as one writer.
4. A commit batches ten records; crash after seven does not skip the remaining three.
5. A subscriber applies entry 9 before entry 8; its contiguous cursor does not falsely cover 8.
6. B's dependency is absent locally; ingestion continues while the dependent view reports pending input.
7. A citation is unresolved or cyclic; this does not fabricate a causal-order failure.
8. A new stream appears after catalog observation; an earlier frontier does not falsely assert completeness for it.
9. A cancellation request races a result; request intent, executor outcome and effect outcome remain distinct.
10. A policy closes publication while a stale writer pushes; the specified host/profile boundary determines admission, without inventing fencing.
11. A channel closes but history remains readable; another channel expires without claiming physical erasure.
12. A label is reused for a new channel; old cursors and permissions do not transfer by accident.
13. An unknown optional record is retained; an unknown authority-bearing rule prevents an unqualified authoritative-state claim.
14. Two replay orders produce the same understood view while retaining conflicting scientific claims.
15. A push response is lost; reconciliation distinguishes accepted, absent and still uncertain without creating a new intent.

The strongest next step is a small set of representation-independent traces like these, then checking whether each candidate encoding can express them without hidden state. Naming should follow those contracts. This may reveal an architectural revision; no existing draft is exempt.
