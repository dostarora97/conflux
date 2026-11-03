# Prior-art lessons + a coherent semantics proposal — tpp-claude v1

Draft for peer review (codex) and the human. Mines the previous session's prior-art research (`matrix-git-swarm-research.md` and siblings in the tpp+web-researcher session) and my own knowledge. Goal: learn others' footguns, and propose a *generic, minimal, cohesive* vocabulary. Nothing here reopens approved v3 architecture; it sharpens naming and records lessons.

---

## Part A — Prior-art footguns and the lessons we should not relearn

### A1. The headline: Matrix's security CVEs all live in MULTI-WRITER CONVERGENT STATE RESOLUTION
Matrix resolves disagreeing room state (membership, power levels, config) across a federated DAG with a deterministic **state-resolution** algorithm. Project Hydra (2025) documents **CVE-2025-49090** (a *state reset* that could manipulate membership/access control) and **CVE-2025-54315** (insufficiently enforced unique create event), and the v2→v2.1 rewrite to reduce state resets. The hard, dangerous, repeatedly-patched part of Matrix is *convergent multi-writer state*.
**Lesson (validates our v3):** we avoid state resolution **by construction.** Per-(channel,writer) streams are single-writer (no convergence needed). Channel *state* (membership/labels/policy) changes through a **single serialization point** (authoritative conditional-write / CAS), never a multi-writer merge. We should state this as a first-class principle: *no convergent state, ever — state changes are serialized operations, not merged histories.* That single choice deletes Matrix's entire worst attack surface.

### A2. Separate four things Matrix keeps distinct (conflating them = CVEs)
- **Stable identity** (opaque, immutable — e.g. room ID from create-event hash) vs **mutable alias/label** (human-friendly, can drift — validate, never treat as identity).
- **Keyed state** (a `(type, key)` map, each entry *replaceable*) vs **timeline** (append-only records, never replaced). State is relative to a graph position, not a wall-clock "latest file."
- **Membership** vs **access to old history** vs **key distribution** — three different concepts.
- **Authorization** (power levels + version rules) vs **sender-supplied role** — never trust a sender's claimed role.

### A3. Two membership axes (XMPP XEP-0045)
Durable **affiliation** (owner/admin/member/outcast) vs transient occupant **role** (moderator/participant/visitor). Maps to our split: **enrollment** (durable: who is catalogued) vs **presence** (transient: who's live now). Keep them separate; presence is an *observation*, never proof of liveness.

### A4. Delivery-stage conflation (Akka/Kafka)
The event journal is NOT the incoming mailbox; publication ≠ delivery ≠ processing. Kafka consumer-groups *load-balance* partitions — independent subscribers need *separate* offsets or they **compete instead of each receiving everything.** Our rule (independent subscriber fan-out, per-subscription cursors) is exactly the anti-footgun; the optional attention-layer note already encodes the full stage split.

### A5. Hosted-Git rate reality (concrete, bites at 1000 agents)
GitHub *recommends* ≤5,000 branches, **≤15 Git reads/s/repo, ≤6 pushes/min/repo** (policy, not a universal Git limit; enforced: 2 GB push, 100 MB object). 100 agents polling every 2 s ≈ 50 fetches/s — already over the recommended read rate. **Lesson:** batch + jitter polling, group fetches, shared local-ingress fan-out (v3 A.2). This is arithmetic, not a measured failure, but it's the first wall on hosted Git.

### A6. Filtering is a view, not a boundary; and causal closure must survive filters
`ls-refs` ref-prefix: the server *may* return extra refs — filtering is an optimization, **not access control**. And a topic/room filter must not discard the causal/auth/control records needed to interpret the selected ones — fetch metadata closure or fetch-on-demand by reachable ID. (We hold this: reserved/control classes and chain validation are not filtered away.)

### A7. Honesty constraints others learned the hard way
- Redaction/tombstone vs immutability: append-only history conflicts with hard erasure — handle honestly (we do: unreachable ≠ erased; host GC separate).
- No instant finality / no identical disconnected views (Matrix optimistic state) — we promise neither.
- A graph is *potential causality*, not proof all communication was included — reply/thread are semantic, not delivery guarantees.

**Sources already in the previous session's `matrix-git-swarm-research.md`** (Matrix spec v12, Project Hydra, IRC RFC 2812, XMPP XEP-0045, Akka, Kafka, reftable, GitHub limits, git-interpret-trailers). codex's `research.md` has 64 more (git-bug, Radicle, Nostr, SSB, ActivityPub, Lamport/CRDT) — those are the ones I have NOT mined; codex should surface footguns from them.

---

## Part B — A coherent, generic, minimal semantics (proposal, not a decree)

**Design rules for the vocabulary:**
1. *Minimal description, maximal capture* — one generic word should subsume many niche cases.
2. *One universe* — antonyms/synonyms/metaphors cohere (reader↔writer, publish→consume, position→frontier).
3. *Load-bearing but not niche* — precise, yet not welded to chat connotations.
4. *A semantic mistake is an architectural mistake* — if a word implies the wrong model, the word is a bug.

### B.1 The core nouns (collapse niche terms into generic ones)
| Generic term | Subsumes (niche terms it replaces) | Why it's the right word |
|---|---|---|
| **channel** | room, DM, broadcast, role-request | A locus that carries records between parties. DM = 2-party channel; broadcast = wide-membership channel; role-request = a channel. *One concept, four uses.* (Telecom/info-theory universe — generic, not "room"=chat-niche.) |
| **stream** | per-writer branch, outbox, per-(room,writer) ref | A single-writer append-only sequence *within* a channel. Kills "outbox" (a mail-universe intruder). |
| **record** | message, event, commit payload, measurement, report, artifact-publication | One immutable published unit, content-typed. Generic across prose/event/data. |
| **writer / reader** | producer/consumer, sender/recipient, author/subscriber | Maximal-generality antonym pair; avoids Kafka-niche "producer/consumer." |
| **position / frontier** | offset, cursor, watermark | *position* = a point in one stream; *frontier* = the boundary set of positions a reader has consumed across a channel's streams (poset-exact — a frontier IS the boundary of a down-closed set). |
| **descriptor** | manifest, state.json, room state | A channel's keyed, serialized state (membership/labels/policy). "Manifest" implied a static bill-of-materials; "descriptor" is mutable-state-via-ops. |

### B.2 The stage verbs (one cohesive pipeline; load-bearing but generic)
`publish → ingest → deliver → attend → effect`
- **publish**: a writer appends a record to a stream; the authoritative ref update makes it durable/visible.
- **ingest**: a reader fetches + validates + durably retains it (raw reception; candidate→verified).
- **deliver**: it enters an interested subscription (routing/fan-out).
- **attend**: it is surfaced for processing (a model turn) — *optional layer*.
- **effect**: an external action results — *separately keyed idempotency*.
Each negation is clean (unpublished / un-ingested / undelivered / unattended / no-effect) — one universe. This IS the Akka/Kafka anti-conflation lesson, named.

### B.3 The lifecycle/identity words (kept on separate axes — the Matrix lesson)
- **identity** (stable, immutable: channel-id, writer-id, incarnation) vs **label** (mutable, advisory, human-facing). Never let label be identity.
- **enrollment** (durable relationship: enrolled → departed → removed; `removed` terminal) vs **presence** (transient: present / absent / unknown — an observation, bounded-expiry, never proof).
- **following/subscription** (a reader's local interest + cursor) — distinct from enrollment (you can read a channel's records without being an enrolled writer, and vice versa).
- **state change = operation** applied via CAS at one authority — NOT a merge. (A1.) Antonym of a safe serialized op is a "resolved" merge — which we forbid.

### B.4 Candidate/verified/retention words (already cohesive — keep)
`candidate → verified` (observation promotion); `open → sealed → archived → expired` (lifecycle, order matters); four retention metrics stay distinct (logical fetchability / active refs / reachable bytes / physical storage).

### B.5 Semantic mistakes we're correcting (= architectural fixes)
- Drop **outbox** (implies per-sender mailbox; wrong under channel/stream model).
- Rename **manifest → descriptor** (implies static list; it's serialized mutable state).
- Prefer **channel** over **room** (generic vs chat-niche); DM/broadcast/role are *not* new nouns, just channel shapes.
- Prefer **position/frontier** over **offset** (offset implies a dense integer index Git doesn't have; position is an OID, frontier is a set).
- Keep **record** over **message** (message implies human prose; record is content-agnostic).

---

## Part C — What I'm asking codex
1. Mine your 64-source `research.md` (git-bug, Radicle, Nostr, SSB, ActivityPub, CRDT/Lamport) for footguns NOT in Part A — especially: Nostr relay/event-id replay, SSB feed-fork (the "you can't have two devices on one feed" footgun), git-bug operation-pack merge semantics, Radicle COB identity/replication. Those are exactly the single-writer-stream and identity lessons we care about.
2. Challenge Part B. Where is a term still niche, non-generic, or implying the wrong model? Is "channel" too Slack-flavored; is "frontier" too mathematical to be ergonomic; is collapsing DM/broadcast/role into "channel shapes" hiding a real distinction?
3. Confirm or break A1 (no-convergent-state principle) — is there any channel-state change in our design that secretly requires a merge rather than a serialized op?
