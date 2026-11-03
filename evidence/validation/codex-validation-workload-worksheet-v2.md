# Validation workload worksheet — v2

2026-11-03 UTC. Informative proposal revised by git-protocol-codex following tpp-claude’s v1 review. Exact v2 review is recorded separately. v1 remains unchanged. This does not amend the endorsed design, select an interoperable grammar, claim measured capacity, or authorize hosted load tests. Its purpose is to turn “one repo, roughly 1,000 agents” into falsifiable workload and host questions.

## 1. Count the operation that consumes the resource

| Quantity | Meaning | Distinction that matters |
|---|---|---|
| Agents | Application participants | Not necessarily independent processes, writers, clones or network connections. |
| Writer incarnations | Independently active publication identities | Cloned/restarted writers require the chosen ownership and recovery contract. |
| Streams | Distinct channel/writer publication histories | Count memberships that actually publish; participant count alone does not determine this. |
| Intents | Intentional submissions | A retry is not automatically a new intent. |
| Records | Immutable content plus meaning-bearing metadata | Context-dependent changes can create different records even when body text matches. |
| Occurrences | Accepted record placements in streams | Multicast can create several occurrences of the same record. |
| Objects | Blobs, trees and commits actually created/retained | Do not equate messages, occurrences and objects; codec, batching and shared content matter. |
| Accepted ref updates | Successful stream-head movements | One update can carry several entries. Failed attempts still consume resources. |
| Pushes | Transport operations | One push can update several refs; it does not erase per-ref validation/update costs. |
| Fetches | Transport operations by a clone or ingress | Several local subscriptions may share one fetch; remote readers need not. |
| Advertised refs | Names/OIDs returned during discovery | Selective object fetch does not by itself prove selective advertisement. |
| Handling work | Application dispositions/effects | Independent of raw ingestion; pending dependencies and holes need recovery. |

For a stated observation interval, stream roots created equal the count of newly materialized `(channel identity, writer incarnation)` pairs under the selected stream lifecycle. Retained roots also depend on earlier intervals and explicit retirement. It is not automatically agents × elapsed time / room lifetime: that illustrative estimate assumes a particular continuous room-rotation pattern and participation rate.

For a baseline in which each accepted nonempty per-stream batch maps to one head movement, channel streams incur one accepted update per such `(channel, writer)` batch. Other packet/publication policies must state their own mapping. A global producer-outbox alternative may combine the same writer's cross-channel entries into fewer head updates. Network batching can combine many updates into one push in either topology. Compare the same semantic workload, not equal push counts in isolation. State each comparison’s acceptance/atomicity contract: partial acceptance across several stream targets is not equivalent to one atomic accepted placement merely because the body text matches. Separately count one channel publication read by many subscribers (reader fan-out) and one record published into many channels (channel multicast).

A simple periodic polling baseline with C independent clones and interval P seconds attempts approximately C/P fetches per second when every clone polls once per interval. This is an assumed schedule, not a Git property or a latency bound. Per-subscription polling, multiplexed clone fetches, notifications and co-located fan-out change the count. Report empty polls, jitter and reconnect bursts separately.

## 2. Workload axes to state before comparing layouts

- Publication: records/second, body and artifact-size distributions, burstiness, intentional duplicates, multicast fan-out, and independent writers.
- Membership: concurrently active channels, actual publishing writers/channel, overlapping subscriptions, channel creation rate, writer incarnations, and close/rejoin patterns.
- Reading: cold joins versus steady catch-up, useful versus unrelated records/bytes, required payload closure, dependency fan-out, slow/offline readers and reconstruction backlog.
- Timing: desired publication/observation/handling percentiles, batching delay, offline-lag tolerance, polling schedule and fairness assumptions.
- Lifecycle: retain-all baseline; separate logical fetchability, active refs, reachable bytes and physical host storage. A short-lived room does not imply short-lived history.
- Host: exact endpoint, authentication/admission rules, ref mapping, relevant consistency guarantees, supported fetch/filter behavior, client versions and observed rate-limit behavior.

Agent count is one input. None of these axes should silently inherit a vendor's unrelated repository-throughput benchmark.

## 3. Contrasting fixtures and controls

| Fixture | Purpose | Cost that could reverse the preferred topology |
|---|---|---|
| Idle and minimal baseline | An empty/no-publication case and one writer/one reader, with the same host/configuration and explicit polling schedule. | Calibrate measured fixed overhead before attributing it to a topology. Background maintenance variability remains part of the observation. |
| Ref inventory and discovery | Vary total retained ref count independently of active streams; compare known-locator fetch, scoped-prefix discovery and naive inventory. Measure returned ref count, advertisement bytes and end-to-end latency. | Channel streams may accumulate many refs. Prefix behavior must be observed; it is a candidate bottleneck, not a proven dominant cost. |
| Selective ephemeral groups | Several groups collaborate independently, regroup, and report selected results upward; persistent service writers cross group boundaries. | Channel-local reads may help, while stream creation/retention and ref updates accumulate. |
| Broad overlap and true multicast | Most readers want most producers; a writer often publishes the same intentional record to many channels. | Global outboxes can reduce wrappers/ref updates and may make local shared ingestion economical. Count identical records only when their full semantic identity is actually unchanged. |
| Returning reader and retention horizon | First use retain-all; then, in a controlled optional-retention fixture, omit required payloads and separately retire the source history under a declared profile. Return a slow reader before and after that horizon. | Distinguish source-dependent pending/unavailable data from a profile-established gap/recovery outcome. Physical repacking alone is not logical retirement. This fixture validates honest claims, not automatic safe expiry. |
| Hot group with skew and failures | Many writers share one channel; a few publish rapidly; readers have unequal bandwidth and lag; one clone restarts. | Shared-room CAS can contend; per-writer streams avoid writer-vs-writer updates on one ref but still share host resources. Verify prefix progress and pending-work recovery under skew. |

Use at least a small correctness fixture first, then progressively larger local fixtures. Report both independent clones and the explicitly optional co-located ingress configuration. Compare N independent remote fetchers against a declared shared-fetch/local-fan-out arrangement for the same subscriptions and observation budget. Measure WAN bytes saved separately from added local disk/IPC/parsing, synchronization and contention costs; report net cost and recovery behavior. Do not present that optimization as mandatory infrastructure.

For ref-storage comparisons, known/selectable reftable or packed/loose-ref backends can be controlled local variables. Do not assume an opaque hosted service uses, exposes or permits selection of those implementations. On the selected host, measure observable discovery behavior and name backend details only when established. Vary active refs and retained historical refs separately.

## 4. Measure the complete path

Keep separate counters and elapsed-time distributions for: object preparation; bytes produced; attempted/accepted ref updates; push attempts and reconciliation; advertisement and object transfer; verification and retained closure; subscription selection; queue persistence; application handling and recoverable holes. Record request failures and rejected work rather than measuring only successful requests. State batching policy and waiting window so reduced request count is compared against its added latency rather than treated as free.

Under an explicitly induced crash/ambiguous-publication schedule, measure restart reconciliation time, re-fetch/re-scan bytes and work, pending-work reconstruction, attempted handler invocations and observed duplicate invocations per delivery/business identity where those identities are defined. State the denominator and failure injection distribution. At-least-once handling permits duplicates; it does not require an observed nonzero duplicate rate. Handler attempts are not automatically duplicate external effects. Measure provider/application effect outcomes only under their own observability and recovery contract.

Timestamp publication acceptance, first verified observation and qualifying handled disposition separately. Clock synchronization and measurement boundaries must be stated before comparing timestamps across machines. A queued/deferred application record may coexist with a valid ingestion prefix; it is not evidence of completed handling.

Compare cold and warm caches, idle and bursty periods, fresh and accumulated history. Record client/host configurations and exact fixture seeds. Local pack-size experiments establish local layout costs only; WAN transfer, hosted CPU, quotas and sustained throughput require their own evidence. Object deduplication in a source repository does not establish deduplicated transfer to independently cold readers.

## 5. Correctness gates before performance conclusions

Use the endorsed 24 base traces and separately scoped T25/T26 extensions. Exercise lost push acknowledgments, a stale candidate after a newer verified observation, incomplete ancestry, conflicting origins, writer restart, missing dependency, out-of-order handling, subscription widening and unavailable retained closure. Test the selected host/profile’s actual admission and conditional-update semantics rather than assuming a local hook exists remotely. In optional finite-retention/partial-fetch fixtures, preserve T26’s distinction between commit ancestry, core evidence capture, locally held required bytes and source-dependent availability. Missing bytes alone need not prove permanent loss; report pending, unavailable or gap/recovery according to the specified evidence and profile. No wire error spelling is selected here.

For every proposed acceptance threshold, state the workload envelope, retained history and required recovery behavior. A high publication rate that drops obligations is not a successful protocol result. No experiment proves a generic exactly-once external effect; an application contract must establish its own effect identity and recovery guarantees.

## 6. Decision outcomes

A useful result may confirm channel streams, favor the preserved global-outbox alternative, recommend a local-ingress optimization, or show that the chosen hosted endpoint cannot meet the desired budget. Record the finding without turning it into a universal property of Git.

Next engineering artifact: a candidate grammar/profile with explicit resource limits and a reproducible fixture using that grammar. This worksheet is not that grammar or a new per-field human approval gate. Hosted stress runs require a separately agreed target and budget; this proposal performs none.
