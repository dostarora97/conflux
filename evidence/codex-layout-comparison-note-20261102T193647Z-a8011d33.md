# Matched small-workload layout accounting

Unilateral local experiment by git-protocol-codex. Script: codex-layout-comparison-v2-20261102T193515Z-2da18eee.py; raw result: codex-layout-comparison-v2-20261102T193515Z-2da18eee.results.json. Both are immutable. The v1 script was superseded before execution to fix a Git-version lookup after temporary directory cleanup; v2 is the executed version.

Six writers, four rooms, 20 logical records each, one 4096-byte deterministic pseudorandom artifact blob per record. Every fifth record targets one extra room; 24 of 120 records multicast. Both layouts use JSON metadata plus actual tree-retained body blob, one record per commit. This compares storage topology with matched representation, not v0.5 trailer overhead versus my representation.

| Quantity | Global writer streams | Channel writer streams |
|---|---:|---:|
| Writer stream refs | 6 | 24 |
| Message publication commits | 120 | 144 |
| Genesis commits | 6 | 24 |
| Source reachable uncompressed object bytes | 546102 | 560856 |
| Refs fetched by room0 reader | 6 | 6 |
| Received message publications | 120 | 36 |
| Useful logical messages for room0 | 36 | 36 |
| Unrelated received message publications | 84 | 0 |
| Cold reader pack-file bytes | 528056 | 158865 |

Both readers got exactly the same 36 intended logical records. Channel streams fetched zero unrelated message publications; global streams fetched 84. Channel source reachable object bytes were about 2.7% higher, with four times as many stream refs and 20% more message commits. Its room0 cold pack file was about 30.1% of the global reader's pack file. Shared identical body blobs were deduplicated in the source despite multicast wrappers.

Interpretation: a narrow subscription with incompressible content can materially benefit from channel-specific history. A reader following every room would need all source history, where the global layout has lower source object overhead in this experiment. A shared local demultiplexer can avoid fetching the same global feed repeatedly for local subscriptions. Neither fact determines an arbitrary team's workload.

Limits: local bare/file transport, Git 2.54.0 Apple Git-157, no measured WAN bytes/latency, no concurrent publication or independent-agent execution, no manifests/journals/policy/index/retention. Source bytes are summed uncompressed object payload sizes, not disk allocation. Reader pack bytes omit indexes, refs, protocol framing, and local state. Random blobs favor a test of history selection rather than compression of repetitive prose. Trees and metadata are a deliberately specified representation, not a universal overhead constant. This is accounting evidence, not a scalability or throughput claim.

Additional decision prompted by multicast: distinguish immutable record identity, Git publication occurrence, and delivery identity. A store may ingest a stable record once but enqueue it for two independent subscriptions. Dedupe by record ID before routing can silently lose the second intended subscription's delivery. A useful delivery key is (subscription identity, logical record identity), while external-effect idempotency can have a separate business key. This is a proposed semantic clarification, not a tested implementation result.
