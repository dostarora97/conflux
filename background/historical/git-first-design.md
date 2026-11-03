**A fresh Git-native protocol for shared communication**

Design exploration, 2 November 2026. This note supersedes earlier suggestions that tasks, acceptance, convergence, or agreement belong in the baseline. It assumes a private team-owned Git service, trusted team participation, and the ability to install receiver-side enforcement. GitHub is an optional host/interface, not a fundamental dependency.

The goal is a general substrate for addressed records, channels, and independent publishers. Humans, agents, scripts, and other programs can participate. A channel may host conversation, status, findings, files, application events, or a domain-specific protocol. No particular workflow, turn-taking rule, completion state, or agreement mechanism is mandatory.

**A good protocol gives a small set of operations clear meaning across very different interaction speeds.**

The baseline should make publication durable, independent writers practical, selective synchronization predictable, records addressable, replay safe, and unsupported behavior visible. It should specify enough to make two independent implementations interoperate. It should avoid requiring every participant to run the same language runtime, model, editor, scheduler, or orchestration framework.

Its main obligations are mechanical: where data lives, how publishers advance it, how readers discover changes, how a record is addressed, how routing works, and what happens when history is no longer available. Higher-level applications can interpret the body and content type.

| Fundamental mechanism | Application-specific meaning that can be layered above it |
|---|---|
| Publish a typed record | Chat message, observation, task, vote, approval, metric |
| Reference another record | Reply, correction, dependency, citation, reaction |
| Follow a channel | Participate in a team, monitor a project, consume a feed |
| Retain or retire history | Audit policy, ephemeral conversation, knowledge preservation |
| Advertise an extension | A2A adapter, task model, agreement model, live transport |

**Git provides objects, history, named publication points, and transfer. The protocol assigns collaboration meaning to them.**

| Git concept | Useful role | Boundary |
|---|---|---|
| Blob | Record body, metadata document, attachment | A hash is an address/integrity identifier, not delivery or retention by itself. |
| Tree | A structured packet containing metadata, records, and attached blobs | A tree may represent one batch rather than a cumulative transcript. |
| Commit | Immutable publication packet plus ancestry | Commit timestamps are not a distributed ordering authority. |
| Parent commit | Previous packet in a writer stream | Parents also expand fetch/retention closure; use deliberately. |
| Multiple parents | Combine selected stream histories into a channel view/checkpoint | A merge is structural inclusion, with no built-in agreement meaning. |
| Ref | A discoverable moving pointer to a stream or descriptor | Names are mutable unless enforcement constrains updates. |
| Slash-separated ref name | Group related refs and support prefix selection | It does not create inherited group membership or branch semantics. |
| Annotated tag | Label an archive or fixed checkpoint | A tag name can still be replaced/deleted without an enforced policy. |
| Fetch refspec | Synchronize selected channels/streams | All required history reachable from selected commits is relevant to transfer. |
| Negative refspec | Exclude streams from a broad selection | This is ref selection, not arbitrary record-content filtering. |
| Object deduplication and packfiles | Avoid resending shared content and compress retained histories | High churn, many refs, and frequent pushes still incur costs. |
| Partial clone/filter | Optionally defer attachment bodies | Requires support and does not define channel semantics. |
| Shallow history | Bound initial history depth in supported situations | Incomplete ancestry needs explicit handling during replay and recovery. |
| Sparse checkout | Limit materialized working files | It does not by itself limit fetched history. |
| Notes | Add separately maintained annotations to existing objects | Needs explicit synchronization and is not inherently a scalable channel. |
| Trailers | Human-readable key/value hints in commit messages | Configuration and formatting rules must be controlled for machine interpretation. |
| Bare repository | Run the protocol without touching an agent's code checkout | A bare store still needs retention and maintenance policies. |
| Worktree | Optionally expose a human-editable channel projection | A working tree is not necessary for the protocol. |
| Update-ref / expected old OID | Local conditional ref updates and transactions | Local operations are not remote transactions. |
| Atomic push | Publish several ref changes together when supported | No cross-repository or external-action transaction follows from it. |
| Receive hooks | Validate publication and ref changes on the team server | Cross-ref policy races need an admission/transaction design. |
| Reflog | Local recovery/debugging of ref movement | Not the shared message-delivery ledger. |
| GC / maintenance / packed refs | Manage retained object/ref storage | Deletion policy must identify all roots keeping history alive. |
| Bundle | Offline export/import of selected retained history | Bundle prerequisites and retained refs need to be explicit. |
| Remotes | Use different transport locations for the same protocol | Independent authoritative control writers across mirrors need extra coordination. |
| Replace / rebase / cherry-pick | Local experiments and transformations | They must not silently change the meaning/identity of published protocol records. |

These are adaptations of Git's [data model](https://git-scm.com/docs/gitdatamodel), [commit construction](https://git-scm.com/docs/git-commit-tree), [fetch behavior](https://git-scm.com/docs/git-fetch), [partial clone](https://git-scm.com/docs/partial-clone), [sparse checkout](https://git-scm.com/docs/git-sparse-checkout), [notes](https://git-scm.com/docs/git-notes), [trailers](https://git-scm.com/docs/git-interpret-trailers), [ref updates](https://git-scm.com/docs/git-update-ref), [push](https://git-scm.com/docs/git-push), [hooks](https://git-scm.com/docs/githooks), [reflogs](https://git-scm.com/docs/git-reflog), [maintenance](https://git-scm.com/docs/git-maintenance), [packed refs](https://git-scm.com/docs/git-pack-refs), [bundles](https://git-scm.com/docs/git-bundle), and [replacement objects](https://git-scm.com/docs/git-replace).

**Commit metadata can be used directly without making arbitrary raw headers the application schema.**

A commit has structured Git headers, a tree, parents, authorship/committer metadata, and a message. Additional metadata can be carried in raw headers, commit-message trailers, or blobs referenced by the tree. A local experiment verified that a custom raw header survives ordinary Git object transfer, and that Git's trailer parser can read a channel hint. This does not establish preservation through all history-rewriting tools.

The practical choice is an authoritative metadata blob in the tree, with optional readable trailers for inspection. This handles nested data, multiple records, attachments, and versioned extensions cleanly. Standard Git object transfer preserves the original bytes. If trailers duplicate authoritative fields, the specification must define matching requirements or precedence; two equally authoritative copies are undesirable.

**Three storage topologies are credible.**

| Option | Publication model | Strength | Cost |
|---|---|---|---|
| A. One log per channel | Every participant appends to the same ref | Very small model; one channel cursor and publication order | Concurrent writers need retries; fast writers can repeatedly beat slower ones |
| B. One writer stream per channel | Each producer advances its own channel-specific ref | Independent writers, straightforward selective fetch, offline publication | Readers follow multiple tips; cross-writer presentation order is derived |
| C. Independent streams plus optional aggregate views | Option B, with periodically built channel checkpoints | Writers remain independent; readers can bootstrap through one captured view | Optional collector/index builder and more retention roots |

Option A is suitable when a channel has few writers or requires one authoritative publication order. It should remain a serious low-complexity alternative, not be dismissed merely because contention exists.

Option B is the strongest general baseline for the stated fast/slow and large-group scenarios. Its base semantics do not require a collector. Option C is a compatible optimization if aggregate views are independently verifiable and their absence cannot block writers or recovery.

A separate ref per individual message is another possible layout, but it grows ref discovery and retention management with message count. A separate repository per channel can help with very different storage lifecycles or server administration; it adds repository management and loses within-repository object sharing. Both are useful specializations rather than initial defaults.

**Channel-specific streams align the storage boundary with the subscription boundary.**

If an agent writes every topic into one global parent chain, fetching its latest message about group A also brings the ancestry containing group B. Filtering the UI afterward does not avoid that history dependency. Putting all channels into one cumulative commit tree creates a related problem.

The proposed unit is therefore a stream for one producer in one channel in one retention epoch:

```text
refs/collab/v1/channels/<channel-id>/meta
refs/collab/v1/channels/<channel-id>/epochs/<epoch-id>/writers/<producer-id>/head
```

This is a proposed namespace. Git can transport custom refs between ordinary bare repositories; it is not automatically supported by every hosted provider. A host adapter can map the same layout beneath `refs/heads/` where necessary, with that mapping explicitly identified.

Each writer normally has a single-parent packet chain within that channel/epoch. Cross-channel replies and citations are ordinary record references rather than Git parent links. They can be followed explicitly when wanted. This makes cross-channel history import an intentional choice.

A descriptor defines a stable channel ID, display name, optional parent-channel alias, supported core version/extensions, write policy, retention mode, current epoch, and optional discovery hints. Those values are examples of channel policy, not all mandatory fields in every deployment.

Git's ref names use slash-separated paths, but names such as `engineering` and `engineering/backend` do not establish inheritance. Also, a ref at a path and another ref below that path cannot be assumed to coexist. Fixed leaves such as `/meta` and `/head`, or opaque channel IDs with separate human aliases, avoid that collision. [Ref-name rules](https://git-scm.com/docs/git-check-ref-format)

Git's separate `gitnamespaces` feature concerns server-side namespace handling. It is not required merely to use a `refs/collab/` prefix. [Git namespaces](https://git-scm.com/docs/gitnamespaces)

**A commit can carry one record or a bounded batch.**

An illustrative packet tree is:

```text
packet.json
records/
  0001.json
  0002.json
objects/
  design.txt
  result.json
```

The packet identifies its version, channel, producer, epoch, and ordered record list. Record fields can include a stable ID, content type, optional routing hints, references, and inline or blob-backed content. The commit parent connects it to the writer's previous packet. A root packet begins a new stream/epoch.

One record per commit offers immediate visibility and easy inspection. Batching amortizes commit and push overhead for fast producers. Both preserve record identity. A batch should be bounded and durable before it is acknowledged locally. A client can choose flush-by-size and flush-by-time rules; those are policy knobs rather than mandatory global constants.

Logical record IDs should remain stable if an archive is repackaged or retained in a new tree. A Git OID can identify the original stored object, while a separately defined record ID supports retries and representation changes. If cross-object-format migration is a goal, avoid assuming every OID is a 40-character SHA-1 string. Duplicated content and repeated intentional messages also need distinct treatment: identical attachment bytes may deduplicate, while two intentional identical messages can have different record IDs.

**The listed collaboration scenarios map to a few independent mechanisms.**

| Scenario | Proposed behavior |
|---|---|
| Fast publisher | Batch records and push its own stream; do not wait for all readers |
| Slow publisher | Publish independently without racing for a shared channel tip |
| Slow reader | Resume each followed stream from a durable commit/record cursor |
| 100-person group | Follow that channel's producer refs; publish once into the channel |
| Many groups | Maintain independent channel subscriptions and cursors |
| Only selected groups | Fetch selected ref prefixes, then optionally apply record-level filters |
| One-to-one conversation | Create a channel addressed to the two participants; reuse core mechanics |
| Join | Discover descriptor and refs; choose start-at-head, retained history, or checkpoint |
| Invite/add participant | Publish a routable invite; change the roster only if the channel uses one |
| Leave | Stop following; optionally publish a leave indication and close writing participation |
| Rejoin | Resume a retained cursor or explicitly choose a new starting point |
| Rename or organize groups | Update aliases/parent metadata while keeping stable IDs |
| Subgroup | Create another channel with an optional relation to its parent; inheritance is explicit |
| Reply across groups | Reference the original record without forcing a cross-group Git parent |
| Small message | Publish a record with a small text body |
| Large artifact | Store a referenced blob/tree; optionally use lazy-fetch capabilities |
| Broadcast | Publish once in a followed announcement channel; no per-recipient copy is required |
| Experiment/fork | Create a new channel referring to a chosen frontier; decide whether history is structurally included |
| Stop or archive group | Mark lifecycle state and apply write/retention policy; no universal convergence event |

Direct-address routing does not imply a privacy boundary under the assumed team-wide repository access. No encryption or public-discovery machinery is required by this design.

**Following, membership, and availability must remain distinct.**

Following is a reader's interest configuration. It can be entirely local and require no shared write. Membership is an optional roster or publication-permission policy. Availability is an observation about a running participant. None should silently imply the others.

A group may allow any team participant to write, restrict writers to a roster, or require an invitation. Adding an agent to a roster does not automatically run its process or force it to follow. A runtime adapter can implement invitation handling or automatic subscriptions under local policy.

Leaving may mean only unfollowing, or it may include a shared membership transition. Previously published records remain under retention policy. Rejoining can resume history if it still exists. Presence announcements and read receipts are optional; neither belongs on every publication's critical path.

**Readers need fairness and explicit gaps, rather than one global timestamp watermark.**

Track each stream's last durably ingested commit, plus record progress inside a partially handled packet if necessary. New producer streams are discovered independently of their author timestamps. Use ancestry to enumerate changes and detect unexpected history replacement. Persist raw ingestion separately from application processing when a record waits for referenced data.

A channel does not have to impose a single semantic order across all publishers. Preserve per-producer order and explicit reference relationships. A UI may use deterministic tie-breaks for display without treating that presentation order as permission, priority, or causality.

Reader scheduling matters in a swarm: a busy stream must not permanently hide a quiet stream. Use a per-stream quota, rotating traversal, and explicit attention policies. Fetching changes and spending LLM context are different budgets. A client may store everything it follows while showing only bounded, relevant slices to its agent.

Reference selection and content filtering also differ. Git can fetch channel refs. It does not natively subscribe to arbitrary JSON predicates or embedding similarity. If a topic needs efficient selective transfer, promote it to a storage-level channel or stream boundary.

**Deletion and retention are protocol choices even when privacy is not a concern.**

| Operation | Effect |
|---|---|
| Hide/mute locally | Changes one reader's view |
| Retract/correct a record | Changes the shared interpretation through another record |
| Remove a file from a newer tree | Removes it from that snapshot; old history can still retain it |
| Retire an epoch | Stops it being part of the current subscription set |
| Keep an archive ref | Preserves reachable history for later readers |
| Delete the last retaining refs and expire other roots | Makes exclusive objects eligible for reclamation |
| Garbage collect | May reclaim eligible objects in that repository |
| Purge retained copies everywhere | Requires coordination with every retaining clone/archive, not one Git command |

The proposed retention unit is an epoch: independently rooted channel-stream segments. Continuing a parent chain across the epoch boundary would keep previous history reachable, so a retention boundary must be deliberate. A descriptor/index can point to archived epochs as metadata without making them Git parents. Any archive refs or aggregate views that still reach old history must be included in retention decisions.

Three useful modes are retain-all, rolling retained history, and current-state-plus-selected-history. A slow reader whose cursor falls below retained history receives an explicit gap with the earliest available epoch/checkpoint. Silent loss disguised as caught-up status is unacceptable.

Epochs are internal storage management. They do not force a conversational session to end or everyone to agree. [Git GC](https://git-scm.com/docs/git-gc) and [bundle behavior](https://git-scm.com/docs/git-bundle) define relevant object retention and export mechanics.

**Optional aggregation can help readers without controlling who may speak.**

A collector can publish a per-channel index or checkpoint containing the exact stream tips it incorporated. It can also construct a commit whose parents include those tips, giving Git a transport/retention root for the captured histories. It need not use a text merge; its tree is constructed from the intended view. Capture sets are explicit rather than claiming to be an instantaneous global latest state.

Readers can bootstrap from that view, then discover newer stream updates. Writers do not wait for the collector. The view is reconstructable from the source streams while they remain retained. Bounded merge fan-in or plain retained indexes may be preferable to repeatedly constructing very large merge commits.

This is a structural aggregation operation. No agreement, approval, or consensus semantics follow from a Git merge. An index containing only OID strings also does not retain the corresponding objects by itself.

**Team ownership makes receiver enforcement practical.**

The receiver can reject malformed packet trees, inconsistent channel/producer identities, unsupported required versions, oversized batches, unauthorized ref changes, and forbidden history replacement. Append-only checks can be stream-local. Lifecycle and retention operations use a distinct authorized path so ordinary writers cannot accidentally erase shared history.

Hooks are code, but can live on the existing Git server without a separate database or message broker. Git's pre-receive hook can reject a receive operation; its update hook can reject individual refs; post-receive can emit hints after publication. [Git hooks](https://git-scm.com/docs/githooks)

Strict cross-ref policies need care. A hook that reads a roster before another concurrent push revokes membership can see stale policy. Strict admission ordering requires an appropriate receiver-side transaction/serialization boundary or an explicitly weaker policy-epoch rule. Atomic push alone does not lock an unrelated policy ref unless the protocol actually includes the necessary checks/updates in the transaction. Likewise, validating a pusher identity requires the team's authentication layer to supply an authenticated principal; Git author text is just metadata.

Separate the ubiquitous wire/storage rules from site policy. Optional hooks may impose record size, rate, sender, retention, and lifecycle limits. A conforming client should surface those rejections clearly and preserve queued publications for appropriate recovery.

**What the local experiments actually establish is deliberately narrow.**

The accompanying script creates temporary bare repositories, uses only local file transport, and removes the repositories afterward. It isolates user Git configuration and does not contact a hosted service. It uses Git 2.54.0 (Apple Git-157), eight concurrent push workers, and limits packing/indexing threads. These are semantic checks, not a production scale or throughput benchmark. The first exploratory run without those thread limits failed the all-pushes assertion; it retained no per-push diagnostics, so the cause was not established. The final results apply to the controlled run.

| Check | Observed result |
|---|---|
| 100 distinct producer-stream refs | All 100 publications accepted |
| 16 sibling candidates for one shared branch | One accepted, 15 rejected without retry |
| Fetch alpha group only | 60 alpha stream commits present, zero unrelated beta commits present |
| Cross-group Git parent | Fetch imported the parent history |
| Cross-group OID stored only in JSON | Fetch did not import that history |
| Descendant commit dates move backward | An ancestry cursor still recovered both unread commits |
| Ref at `engineering` plus ref below `engineering/backend` | Prefix collision rejected |
| Atomic push with one update-hook rejection | The otherwise valid ref was not published |
| Receiver append-only hook against forced replacement | Replacement rejected and original tip preserved |
| Extra raw commit header and ordinary transfer | Original header bytes preserved |
| Standard commit trailer parsing | Channel trailer read successfully |
| Tombstone with old commit as ancestor | Old payload retained |
| Delete final ref before GC | Old payload still present immediately afterward |
| Remove retaining roots, expire reflogs, then GC | Exclusive old payload no longer present in that temp repository |
| Fetch newly rooted epoch only | Old epoch was not required |

All writer publications in this harness originated from one test object database, with distinct refs and concurrent push processes. This does not simulate independent machines, process supervision, or large-network packet loss. It validates the selected Git mechanics and supplies a repeatable starting point for a multi-clone stress test.

**The recommended design is channel-specific independent streams, with optional aggregate views and configurable retention epochs.**

The mandatory core should specify packet representation, record addressing, channel/stream discovery, ref publication, cursor recovery, unsupported versions, and history gaps. Minimal implementations can retain all history and omit collectors. Deployments needing bounded history can advertise the epoch/retention capabilities they require.

Tasks, convergence, agreements, receipts, presence, agent discovery catalogs, semantic routing, and orchestration remain independently negotiated extensions. Familiar agent protocols inform those extensions; they do not determine the core's purpose.

The next prototype should compare option A and option B with independent clones, mixed publishing rates, bounded reader budgets, join/leave churn, and an epoch transition while one reader is offline. The choice should be judged by setup simplicity, retry rate, transfer volume, starvation, recovery behavior, and interoperability. These are the uncertainties worth measuring before increasing the protocol's scope.
