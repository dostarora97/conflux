**Git-backed agent coordination: research and design exploration**

Research date: 2 November 2026. This document examines official specifications, project documentation, source repositories, and original research. It separates documented capabilities from proposed adaptations. It is a design study; the surveyed implementations have not been installed, benchmarked, or audited here. The selection covers the main architectural families and several unusually close precedents, rather than claiming to inventory every agent project.

The subsequent [Git-first design exploration](/Users/I533118/personal/code/agent-coordination-research/git-first-design.md) supersedes this note's initial task-oriented baseline. It treats task management, agreement, and convergence as optional applications, and develops generic channels, independent publication, selective synchronization, membership, and retention from Git primitives. The local Git experiments referenced there are separate from the third-party projects surveyed here.

**The design opportunity is a durable collaboration substrate that independently running agents can use through ordinary Git.**

The desired baseline is an accessible Git remote, existing authentication, and a small client. An agent should be able to publish, disconnect, return later, and reconstruct what happened. Humans should be able to inspect the record. Agents should retain their own execution frameworks and model providers. Richer discovery, scheduling, real-time communication, and review interfaces should be additions that preserve the baseline.

The operational goal is no additional mandatory coordination service. Git hosting is still infrastructure. Git does not execute agents, wake a stopped process, guarantee delivery to a permanently absent recipient, or provide an application-specific agreement algorithm. Those boundaries determine what a small protocol can honestly promise.

**The landscape becomes easier to understand when its layers are separated.**

| Layer | Question it answers | Representative precedents |
|---|---|---|
| Agent access | How does an application invoke an agent or expose a tool? | Agent Client Protocol, MCP |
| Agent interaction | How are tasks, messages, results, and requests represented? | A2A, NLIP, earlier BeeAI ACP, AAMP |
| Discovery and identity | How is an agent described, located, and authenticated? | A2A cards, ANP, OASF, NANDA |
| Execution and orchestration | Who runs work, checkpoints it, and selects the next step? | LangGraph, CrewAI, Microsoft Agent Framework, Gas Town |
| Durable collaboration | What survives process death and concurrent independent publication? | git-bug, Radicle, Git mailboxes, signed feeds |
| Coordination policy | Who owns work, accepts a proposal, or authorizes a change? | Explicit state transitions, task awards, review policies, serialized decisions |

These layers can be implemented together, but combining them in one product does not make them the same problem. A messaging standard can leave storage to its implementer. A persistent workflow engine can still require one application runtime. A Git archive can preserve history without being the live source of coordination state.

**Current agent protocols provide useful semantics without requiring us to adopt their entire deployment model.**

| Protocol or system | What the primary material establishes | Useful adaptation | Operational boundary |
|---|---|---|---|
| [A2A](https://a2a-protocol.org/latest/specification/) | Independent agent interaction through messages, tasks, artifacts, capability declarations, and multiple bindings; latest released version displayed is 1.0.0. | Separate conversation context, task identity, message identity, and output artifacts; represent requests for additional input. | Standard network bindings expose agent service endpoints; publishing a Git event is not automatically an A2A interaction. |
| [BeeAI Agent Communication Protocol](https://github.com/i-am-bee/acp) | The archived repository states that ACP is now part of A2A under the Linux Foundation. | Study its multimodal, asynchronous interaction ideas as historical input. | Treat its current successor relationship accurately when choosing interoperability targets. |
| [Agent Client Protocol](https://agentclientprotocol.com/protocol/v1/overview) | Editor/client-to-agent sessions using JSON-RPC, with requests, notifications, session loading, updates, and cancellation. | Adapt a local coding harness to consume and produce durable coordination events. | A client-agent connection does not itself provide replicated peer mailboxes. This ACP is distinct from BeeAI ACP. |
| [MCP](https://modelcontextprotocol.io/specification/2026-07-28) | The current core connects applications to tools and contextual resources through self-contained requests and negotiated capabilities. | Expose the Git client as a few tools or resources when convenient. | MCP need not be a baseline dependency. |
| [MCP Tasks](https://modelcontextprotocol.io/extensions/tasks/overview) | An optional extension supplies durable task handles, polling, input requests, and cooperative cancellation. | Persist job identity before responding; distinguish cancellation intent from an actual stopped job. | Clients and servers must support the extension; a stored handle still needs an executor. |
| [NLIP / ECMA-430](https://ecma-international.org/publications-and-standards/standards/ecma-430/) and its [message specification](https://ecma-international.org/wp-content/uploads/ECMA-430_1st_edition_december_2025.pdf) | A published application-level interaction standard with structured messages/submessages and separate transport bindings. | Keep the collaboration envelope independent of how bytes move. | A new Git adaptation would need its own conformance analysis; reusing an envelope alone is insufficient. |
| [ANP](https://github.com/agent-network-protocol/AgentNetworkProtocol) | Layered specifications address identity, authentication, descriptions, discovery, and messaging, with release and draft boundaries documented separately. | Separate stable identity from a changing network locator; permit descriptive records and optional identity extensions. | Its web identity and messaging machinery need not become mandatory for a small trusted team. |
| [AGNTCY](https://docs.agntcy.org/) | An ecosystem separates discovery, communications, identity, and observability components. | Preserve clear architectural boundaries and independent adapters. | Adopting the whole ecosystem introduces services beyond a Git client. |
| [OASF](https://github.com/agntcy/oasf) | A schema and taxonomy for agent capabilities, interactions, and metadata. | Allow a rich external capability description to be referenced from a small local descriptor. | Do not require a full taxonomy service just to join a known conversation. |
| [SLIM](https://github.com/agntcy/slim) | Messaging runs through configured SLIM nodes, with client and server modes. | An optional low-latency notification or live interaction transport. | Running nodes is an additional operational choice. |
| [NANDA](https://github.com/projnanda) and [AgentFacts](https://github.com/projnanda/agentfacts-format) | Registry/index infrastructure and machine-readable metadata for locating and describing agents. | Keep advertised capabilities portable; distinguish a capability claim from verified evidence. | Global discovery is a separate problem from exchanging messages among known participants. |
| [CloudEvents](https://cloudevents.io/) | A common event envelope intended to support portable event handling. | Reuse its identity/type/source conventions if they simplify interoperability. | It supplies no task ownership, persistence, ordering, or execution policy by itself. |

The MCP documentation currently redirects `latest` to the 2026-07-28 revision. Its maintainers describe the move of Tasks to an extension and removal of the protocol-level initialization/session handshake in their [August 2026 roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/). Designs based on older MCP articles need to pin their assumptions.

A particularly relevant constraint is that A2A custom bindings must preserve the data model, semantics, errors, and required operations. A small mailbox inspired by A2A should be described that way until it meets those requirements. [A2A custom binding requirements](https://a2a-protocol.org/latest/topics/custom-protocol-bindings/)

**Practical coordination tools reveal which conveniences agents repeatedly need.**

| Project | Documented approach | Design lesson | Fit with a Git-only baseline |
|---|---|---|---|
| [MCP Agent Mail, Rust](https://github.com/Dicklesworthstone/mcp_agent_mail_rust) | Persistent identities, threaded inboxes, acknowledgments, advisory file reservations, a Git archive, SQLite indexing, and MCP/CLI interfaces. Its limitations describe same-machine/shared-filesystem coordination. | Provide an inbox that explains what needs attention; make reservations explicitly advisory. | Useful interface precedent; its server and database model is not distributed coordination through independent clones. |
| [aweb](https://github.com/awebai/aweb) | Durable mail/chat, identity, wake events, federation, and optional team coordination through services. | Separate a durable message from a wake signal; separate identity from a particular running session. | Its live server/registry arrangement is an optional integration architecture. |
| [OATS](https://github.com/awebai/oats) | A provider- and harness-independent team framework built around configurable capabilities and communication. | Team behavior can be shared instructions and contracts above a common substrate. | Its chosen messaging service need not define our core wire format. |
| [Beads](https://github.com/gastownhall/beads) | Dependency-aware task memory, readiness queries, and versioned data through Dolt. Current documentation distinguishes embedded and server modes and treats JSONL as an export. | Model dependencies and actionable readiness; avoid treating a rendered task list as the source of truth. | Current Beads is not simply JSON files committed with ordinary Git; Dolt is an additional dependency. |
| [Gas Town](https://github.com/gastownhall/gastown) | Persistent work identity, isolated workspaces, coordinator roles, and long-lived services. | Preserve goals, context, and work ownership across ephemeral worker sessions. | A workspace manager and orchestrator contributes more operational machinery than the target baseline. |
| [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams) | Independent teammate contexts, mailboxes, shared dependency-aware tasks, local file locking for claims, and completion hooks. | Support direct peer messages and check completion conditions in the harness. | Product-specific execution and local locking are not remote Git coordination guarantees. |
| [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Checkpointers preserve a conversation's graph state; stores preserve information across conversations. | Distinguish an execution checkpoint from long-term shared knowledge. | Agents may use it locally; peers should not need its runtime or serialized internals. |
| [CrewAI Flows](https://docs.crewai.com/en/concepts/flows) | Structured event-driven workflows, state, and task/crew composition. | Explicit event transitions make execution easier to observe and resume. | A workflow policy can run above the protocol without becoming mandatory. |
| [Microsoft Agent Framework orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/) | Sequential, concurrent, handoff, group-chat, and manager-directed patterns. | A communication substrate should support several interaction topologies. | Do not bake a permanent manager or turn-taking scheme into the storage format. |
| [AutoGen](https://github.com/microsoft/autogen) | Historical multi-agent message-passing architecture; current README marks it archived and directs users to Microsoft Agent Framework. | Separate messages, agents, and runtime orchestration; retain ideas without depending on an obsolete project status. | Historical research and architectural precedent. |
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | Role-based software work organized around procedures and intermediate artifacts. | Publish usable contracts and deliverables at handoff boundaries. | Role names and software-company structure are application policy. |
| [CAMEL](https://github.com/camel-ai/camel) | Role-playing and workforce-based multi-agent collaboration. | Allow role-specialized discussion and dynamic teams. | Role simulation is not a distributed delivery or agreement guarantee. |

These examples suggest a useful interface vocabulary: inbox, task, dependency, finding, question, artifact, proposal, acceptance, handoff, and checkpoint. They do not imply that every installation needs all ten features immediately.

**Git-native collaboration has especially close precedents.**

[git-bug's reusable data model](https://github.com/git-bug/git-bug/blob/trunk/doc/design/data-model.md) treats collaborative entities and their histories as data in Git, with authorship, remote synchronization, attachments, and entity-specific edit rules. This is a strong precedent for using Git as application storage while keeping source-code checkouts clean.

Its [DAG specification](https://github.com/git-bug/spec/blob/trunk/dag-entity.md) defines operation packs in commits, logical clocks, deterministic replay, topology validation, and merge behavior. An entity can be a task or proposal rather than a bug. We should examine reuse of that model before designing an equivalent one from scratch. Deterministic field resolution must still be selected for the domain: last-write-wins assignment is not sufficient evidence that an exclusive task was safely awarded.

[Radicle](https://radicle.dev/guides/protocol) stores social collaboration as signed Collaborative Objects replicated with Git, alongside decentralized identity and peer discovery. Its extensibility is highly relevant to sessions, proposals, and decisions. A minimal Git-hosted system can borrow the object model without requiring Radicle's full peer network. Directly adopting Radicle is an alternative if its operational and interoperability choices are acceptable.

Several newer agent projects sit very close to the desired surface:

| Project | Relevant documented design | What to examine next |
|---|---|---|
| [jj-mailbox](https://github.com/MiaoDX/jj-mailbox/blob/main/spec/PROTOCOL.md) | Files as the interface; agent profiles, inboxes, tasks, references, and artifacts, with Jujutsu managing history. | Its small human-readable surface is useful. Jujutsu is an additional dependency, and moving unread files to processed locations needs careful concurrent/replay semantics. |
| [DarkMatter](https://github.com/dadukhankevin/DarkMatter) | Bilateral Git mailboxes, signed identity/contact cards, local/LAN/hosted locators, encrypted bodies, and receipt/recovery machinery. | Examine identity continuity, fetch-without-checkout, and explicit locator trust. Its broader features and security model require independent evaluation before adoption. |
| [Heddle](https://github.com/zyads/heddle) | Git-ref synchronization, advisory editing intent, isolated work, verification before integration, and compare-and-swap adoption claims. | A close precedent for coordinating writers through a shared remote. Its documentation distinguishes unsigned metadata and design-only peer federation from implemented behavior. |

These are architectural references, not evidence of broad adoption or independently demonstrated reliability. Their existence makes reuse and interoperability investigation worthwhile; it does not settle the choice of implementation.

**Older messaging and distributed-data systems explain several of the strongest design principles.**

| Precedent | Relevant mechanism | Adaptation to agent collaboration |
|---|---|---|
| [Email / RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322#section-3.6.4) | Stable message identification and explicit reply/reference relationships. | Threads should survive retransmission and transport changes; physical delivery order should not define reply structure. |
| [AAMP](https://github.com/larksuite/aamp) | Agent task collaboration through existing mail infrastructure, structured lifecycle headers, and human-readable bodies. | A small semantic overlay can make an existing ubiquitous transport useful for agents. A Git variant could pursue the same architectural separation. |
| [public-inbox source README mirror](https://github.com/nojb/public-inbox) | An archive-first email system stored and mirrored in Git, with several reading interfaces. | Treat interfaces as views over portable history. The upstream website was inaccessible to the research browser, so this description uses the project's mirrored source README. |
| [Secure Scuttlebutt](https://ssbc.github.io/scuttlebutt-protocol-guide/) | Signed author feeds containing an append-only previous-message chain, with replication and separately fetched blobs. | A stream per producer avoids a global speaking lock and supports delayed synchronization. |
| [Nostr NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md) | Signed events, explicit kinds/tags, client filters, and relays. | Keep event meaning stable across storage/relay choices, with selective subscriptions. |
| [Block Buzz](https://github.com/block/buzz) | A communication platform represents human and process activity as signed events over a Nostr relay. | Human/agent participation can share one event vocabulary; choose a relay only when its live features justify the infrastructure. |
| [Matrix](https://spec.matrix.org/latest/server-server-api/) | Federated event history has causal links; state changes require explicit resolution. | A merged history and a resolved authority state are separate concerns. |
| [ActivityPub](https://www.w3.org/TR/activitypub/) | Actors have discoverable inbox/outbox endpoints; activities carry typed meaning. | Separate actor, address, activity, and object identities. Adopting its server federation is optional. |
| [Automerge](https://automerge.org/docs/hello/) | Local changes and concurrent merge through a network-independent CRDT library. | Make synchronization independent of presentation and preserve offline work. |
| [Automerge synchronization state](https://automerge.org/automerge/automerge/sync/struct.State.html) | Tracks local, peer, and shared heads rather than relying on wall-clock cutoffs. | Record what a consumer has incorporated; distinguish fetched state from acknowledged state. |

For ephemeral presence and live UI hints, Automerge also separates [ephemeral data](https://automerge.org/docs/reference/repositories/ephemeral/) from durable document changes. We can apply that distinction without adding Automerge as a mandatory dependency.

**Agent research contributes useful interaction patterns, with a different evidentiary status from a deployed standard.**

The original [FIPA Contract Net specification](https://www.eecis.udel.edu/~decker/courses/886f04/pubs/FIPA-ips.pdf) describes solicitation, proposals, selection, rejection, and outcome reporting. A lightweight task award protocol could reuse this shape: publish a request, let capable agents offer, let an authorized actor award, and let the awarded agent report results. Refusal and non-selection are meaningful outcomes; agents should not silently assume that receiving a task description makes them its owner.

[BSPL's original semantics paper](https://www.csc2.ncsu.edu/faculty/mpsingh/papers/mas/AAMAS-12-BSPL.pdf) specifies interaction through information prerequisites and integrity constraints rather than prescribing a centralized control flow. This is a useful basis for our design: a result must reference an accepted request; an acceptance must identify a proposal revision. Agents can act independently when they possess the required information. The adaptation is conceptual; we need not ship a protocol-language interpreter.

[Agora](https://arxiv.org/html/2410.11905v1) investigates combining natural-language interaction with more structured routines for recurring exchanges. Our adaptation would be conservative: let prose support exploration and let validated schemas handle repeated commitments. Any learned convention can become an explicit, versioned contract artifact after review. The base protocol should remain understandable without executing generated routines.

[AECP](https://arxiv.org/html/2610.06481v2), an October 2026 research proposal, makes structured knowledge and interface artifacts actionable through the execution harness. In particular, revised contracts can mark affected consumers stale, and completion can depend on reconsidering the revision. For our system, this suggests optional adapters that inject relevant findings on file access and verify recorded interfaces before accepting work. The paper's experimental results do not establish a universal advantage or general prompt-injection immunity for a Git implementation.

The [MAST research](https://arxiv.org/abs/2503.13657) identifies failure families involving system design, inter-agent alignment, and task verification. Our design implication is to evaluate whether communication changes outcomes: recover unanswered questions, preserve objections, detect stale assumptions, and validate completion. Message throughput alone is an insufficient success metric.

**First principles point toward a small core with explicit extensions.**

1. An independently running participant has a durable identity, but an individual producer process has its own stream identity.
2. A published event has one stable event identity. Retries reuse it. The same identity with different content is a conflict.
3. Artifacts are exact versions, identified by content and retained with an explicit availability policy.
4. Reply and dependency relationships are explicit. Display order is a view over those relationships.
5. The durable record can be replayed into a projection without running an LLM or repeating external effects.
6. A request does not establish acceptance. A worker's claimed completion does not establish independent verification.
7. Publication and processing remain possible at different times. Both sides need not be online simultaneously.
8. The authority to publish a message is separate from the authority to award work or change policy.
9. Optional features advertise their requirements; absent optional infrastructure cannot break core synchronization.
10. A known session locator is sufficient to begin. Global search and discovery can be layered later.

**Causality should be precise while ordinary publication stays easy.**

[Lamport's original paper](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) establishes a partial order of causally related events and logical ordering mechanisms. For the proposed protocol, stream ancestry establishes local publication order; explicit references establish cross-stream dependencies. Scalar logical timestamps can support a deterministic display order, but different timestamps do not prove that one event caused the other. Concurrent events need not have equal scalar timestamps.

Record a frontier when it matters: a map from producer stream to a particular incorporated commit. A proposal acceptance can declare which record it considered. A summary can declare which events it covers. A new finding beyond that frontier is visibly newer information.

The protocol should distinguish at least these stages:

| Stage | Meaning |
|---|---|
| Locally queued | The client has durably recorded an event to publish. |
| Published | The designated remote accepted the relevant ref update. |
| Ingested | A recipient has durably stored the event for processing. |
| Presented | The receiving harness exposed the event to the agent. |
| Accepted | An authorized participant emitted a domain-specific acceptance. |
| Completed | The worker reports the requested result. |
| Verified | The specified evidence or reviewer policy has been satisfied. |

A presented receipt does not prove cognitive understanding. Its honest meaning is a harness assertion about delivery into context. An acceptance is an explicit claim by its author.

**Coordinate only the operations whose invariants require it.**

The [CALM analysis](https://arxiv.org/abs/1901.01930) connects coordination-free consistency with monotonic computation. [Invariant-confluence research](https://www.vldb.org/pvldb/vol8/p185-bailis.pdf) asks whether independently valid changes remain valid when combined. These provide a useful analysis method, rather than a blanket guarantee for our application.

Two independent findings can both be retained. Two independent claims of sole ownership cannot both satisfy an exclusive-owner invariant. A conflict-free event set therefore does not imply conflict-free task authority.

| Operation | Default proposed treatment |
|---|---|
| Add a message, finding, candidate artifact, or objection | Independent append; deduplicated union. |
| Acknowledge one exact proposal revision | Independent authored event; evaluate against pinned acceptance policy. |
| Publish an alternative design | Independent object or branch; preserve provenance. |
| Award exclusive ownership | Serialize through a designated authority/ref, or use an explicitly defined allocator. |
| Change membership or decision policy | Authorized transition under the existing policy. |
| Spend a shared fixed budget or execute a unique external action | Enforced authority and downstream idempotency/fencing as required. |
| Declare a discussion closed because no objections exist | Require a defined review frontier and close policy; silence alone is insufficient. |

A shared authoritative ref can serialize awards. A contender reads state, checks preconditions, creates its candidate update, and publishes conditionally. On a conflict it must fetch and reevaluate the claim. It must not blindly replay its old award on top of the winner. Git offers expected-value ref updates and conditional atomic multi-ref pushes, with support and protection differences documented in [git push](https://git-scm.com/docs/git-push). GitHub's [REST ref API](https://docs.github.com/en/rest/git/refs) has different request parameters, so clients need transport-specific concurrency handling.

The remote becomes the authority for that operation. Two mirrored remotes must not independently award the same exclusive task and later assume Git can reconcile both awards safely. During a partition, agents can continue exploratory work while authoritative awards wait. Leader election, automatic remote failover, or Byzantine consensus would be additional protocols.

**A plausible core is a small mail format, a Git synchronization rule, and deterministic validation.**

The following is an illustrative design, not an existing standard or completed schema:

```json
{
  "version": "0.1",
  "id": "urn:uuid:example-event-id",
  "session": "urn:uuid:example-session-id",
  "actor": "reviewer",
  "producer": "reviewer-instance-9",
  "to": ["architect"],
  "kind": "message",
  "topic": "interface-review",
  "refs": ["urn:uuid:earlier-event-id"],
  "body": "The retry interface needs a stable request identifier.",
  "artifacts": [],
  "extensions": {}
}
```

The common envelope needs very few concepts: version, identity, session, author, intended recipients, meaning, references, and content. Structured task or agreement payloads can be extensions. An optional CloudEvents representation could carry equivalent identity metadata; it should replace redundant fields rather than duplicate every identifier.

Initially, useful event meanings are message, request, response, artifact, and receipt. A task extension can add offered, accepted, input-needed, result, and cancel-requested. An agreement extension can add proposal, objection, acceptance, and decision. We should resist making a large universal agent ontology mandatory before two agents can exchange a question.

My recommended initial task policy is explicit addressing: a requester sends work to a named participant, which explicitly accepts or declines. The requester controls its own task's assignment generations. This removes the need for a global competitive-claim service from the first version. A participant still needs durable deduplication across its own executor instances. Automatic reassignment and external effects require additional generation/authority rules; an offer must not authorize two independent recipients to perform the same unique effect.

A session descriptor identifies its protocol version, participants, stream discovery rule, artifact policy, and any authority/policy extensions. Updates create new descriptor versions. Events that depend on a policy pin its version. Names, capabilities, authority, and current availability remain distinct fields.

**The baseline Git layout should be chosen through a small comparison, not by aesthetic preference.**

| Candidate | Advantages | Costs and questions |
|---|---|---|
| One shared session branch of immutable event files | Easy to inspect; easy export; compact initial client. | Concurrent pushes retry; enforce union and unchanged old events; shared write point. |
| One stream branch per producer/session | Independent publication; simple local order; reduced contention. | Multiple tips and roster discovery; explicit cross-stream causality; stream counts and retention. |
| One collaborative-object DAG per session/task | Reuses strong git-bug/Radicle ideas; object-local replay and merge. | More specialized storage and reducers; ref synchronization across hosts needs validation. |
| GitHub Issue/Discussion as canonical record | Convenient existing UI and APIs. | Git clone does not contain that record; edits, deletions, pagination, and export semantics need handling. |

For a first protocol spike, producer streams are a strong default. Benchmark the shared-branch alternative as the smallest implementation, and inspect git-bug's generic format as the reuse candidate. Choose one mandatory publication profile for interoperability. Multiple optional backends without a common mandatory profile can fragment a small ecosystem before it begins.

An illustrative stream namespace is `refs/heads/agentchat/<session>/<producer>`. Ordinary branches are a practical initial compatibility target. Advanced custom refs need host-specific capability testing. Each stream can contain immutable event files and small attachments; commits may batch several events without changing their identities. Events remain independently addressable inside a batch.

Use a separate bare coordination clone where convenient. Read untrusted peer data as bounded blobs without checking out or executing peer-supplied repository content. Local JSON or SQLite indexes can accelerate inbox and search views, but must be rebuildable from the durable record if they are called caches.

**Recovery behavior is part of the protocol, not an implementation afterthought.**

| Failure or ambiguity | Required proposed behavior |
|---|---|
| Publish succeeded but its acknowledgment was lost | Retry with the same event identity; reconcile publication before creating another logical request. |
| Reader crashes after receiving data | Resume from durable ingestion/processing state; allow safe redelivery. |
| Dependencies arrive later | Retain the event in a pending state; resolve missing references; do not infer a missing event never existed. |
| Agent disappears | Preserve its history and work; treat liveness as an observation; use explicit reassignment policy. |
| Two processes use the same stream | Detect divergent publication; stop and resolve or allocate a new producer identity. |
| A branch is reset or rewritten | Detect ancestry regression relative to remembered tips; preserve evidence and require explicit handling. |
| Unknown optional event arrives | Preserve it and display an intelligible fallback where possible. |
| Unknown event can change authority or completion | Report unsupported semantics; do not claim authoritative state is fully understood. |
| Artifact locator exists but the artifact is unavailable | Show incomplete evidence; do not accept the locator as successful delivery. |
| Work finishes after cancellation/reassignment | Retain the result with its generation; apply current acceptance policy before using it. |
| External effect succeeds but result recording fails | Query the downstream idempotency key/status when possible; otherwise expose uncertainty. |

An ingestion cursor and a task-processing cursor can be separate. An event whose dependencies are missing should not force unrelated work to stop. Advancing ingestion is safe once the raw event and its pending status are durably retained; advancing application processing requires its own durable result.

External effects need their own records and idempotency behavior. This is also an explicit concern in [Temporal's activity guidance](https://docs.temporal.io/activity-definition). Git replay can deterministically rebuild a projection; it cannot guarantee that an arbitrary external action occurs exactly once.

Objects referenced only by a hash string inside JSON are not thereby retained by Git. Preserve artifact blobs through actual trees, history, and archival refs, or define a separate retained storage policy. Unreachable objects may be pruned. [Git garbage collection](https://git-scm.com/docs/git-gc)

**An ergonomic interface should expose decisions and obligations, with synchronization hidden underneath.**

The smallest useful client operations are join, publish, sync, inbox, show, and acknowledge. More domain-specific commands can render the same record as tasks, questions, proposals, or handoffs. Commands should have machine-readable output and human-readable errors. No particular language runtime, MCP host, model, or editor needs to be mandatory.

An inbox can answer:

- Which questions are addressed to me and unanswered?
- Which proposal revisions need my acceptance?
- Which artifact contracts changed since I accepted them?
- Which tasks are unblocked under the current policy?
- Which results are available but not verified?
- What changed beyond my last summary frontier?

These views reduce context cost. All-to-all discussion creates N(N-1) directed relationships for N participants. The protocol should permit direct messages, topics, subscriptions, and artifact-scoped retrieval, while letting a particular team choose a shared discussion when useful. Topic routing and bounded inbox queries should precede sophisticated semantic search.

No durable mailbox can wake a fully stopped process without an executor, scheduler, hook, or running client. The baseline can be manual or bounded polling. A reusable host integration may wake agents, but it must be an advertised runtime capability, not an assumed property of Git.

**GitHub should add convenience while core recovery remains Git-based.**

Issues can present sessions and tasks; pull requests can review concrete changes; checks can show policy/evidence state. A bridge can import human comments as new events while retaining source IDs and revisions, and render agent events back into the interface. Origin metadata and idempotency prevent loops. GitHub labels and project fields are useful views, but should not silently become a second conflicting authority.

Webhooks can prompt a fetch; failed deliveries are not automatically retried by GitHub. Clients must reconcile history regardless of notification success. [Webhook failure handling](https://docs.github.com/en/webhooks/using-webhooks/handling-failed-webhook-deliveries)

Actions workers should drain pending durable work rather than equate a workflow run with one guaranteed queued message. Default concurrency behavior can replace pending runs, and scheduling can be delayed or dropped under load. [Actions concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency), [workflow troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows)

Other practical boundaries include API backoff and conditional polling, workflow-trigger behavior for `GITHUB_TOKEN`, and artifact expiration. GitHub search is not a complete stream index: code search covers the default branch, so a producer-branch design needs its own index or explicit ref discovery. [REST API practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api), [workflow triggering](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow), [workflow artifact retention](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts), [code search scope](https://docs.github.com/en/code-security/reference/security-incident-response/investigation-tools)

**Several useful extensions can remain independent.**

| Extension | Proposed feature | What makes it valuable |
|---|---|---|
| Task exchange | Request, offer, acceptance, dependencies, result, cancellation intent. | Clear obligations without a global manager. |
| Agreement | Exact proposal revision, acceptance policy, objections, and decision evidence. | Verifiable agreement that survives reconnects. |
| Shared contracts | Schema/interface artifacts, registered consumers, revision invalidation. | Prevents implementation continuing against stale agreements. |
| Handoff | Goal, current state, artifacts, unresolved questions, event frontier. | A new worker can resume without inheriting a vendor-specific transcript. |
| Discovery | Rich cards, organization catalogs, external indexes. | Finding collaborators beyond a known roster. |
| Identity | Signed events/commits, authorized keys, key succession. | Portable attribution across hosting boundaries. |
| Live hints | Webhooks, local notifications, optional live transport. | Lower latency while preserving durable recovery. |
| A2A gateway | Map supported task operations onto durable work and result events. | Interoperate with live endpoints without requiring every peer to host one. |
| MCP/ACP adapters | Expose the client inside compatible agent hosts. | Integrate existing runtimes without defining them as the storage standard. |

For identity, Git author names and branch naming conventions do not authenticate a logical actor. A trusted-owner deployment may begin with repository credentials and an explicit participant mapping. Cross-organization operation may need signatures and a policy binding keys to authority. Valid signatures establish authorship/integrity under those assumptions, not correctness of the message or permission to execute it. Branches and recipient fields also do not create repository-level read isolation.

**A disciplined prototype can test the architecture before it grows into a platform.**

Start with two independent clones, a session descriptor, two producer streams, immutable JSON events, small retained artifacts, and a deterministic inbox. Use one standard Git remote. Add task and agreement extensions only after publication/recovery behavior works. Keep policy and data codecs separate from transport and interface code.

The first meaningful tests are histories, not copies of implementation functions:

1. Both agents publish simultaneously without losing either event.
2. A publish acknowledgment is lost; retry does not duplicate the request.
3. A consumer crashes after ingestion but before acknowledgment; it resumes safely.
4. An agent returns after several offline updates and sees all relevant unanswered work.
5. An artifact is referenced before locally available; the client shows a pending dependency.
6. A proposal changes after acceptance; the old acceptance is visibly tied to the old revision.
7. Two agents claim exclusive ownership; one award becomes authoritative and the loser reevaluates.
8. A stale worker returns after reassignment; its result cannot silently become current.
9. Two clients process the same event set in different arrival orders and derive equivalent understood state.
10. Unknown critical semantics produce an explicit unsupported-state result.
11. All notification infrastructure is disabled; eventual synchronization still works when clients run.
12. The local search/projection database is deleted; the client rebuilds it from retained history.
13. Published history regresses; a client that remembers a newer tip detects it.
14. The session is exported and moved to a different Git host without changing its identity.
15. A fresh implementation in another language reads the fixtures and reaches the same projections.

Measure setup steps, synchronization requests, bytes transferred, recovery time, inbox relevance, human relay interventions, and task completion quality. Compare against both the existing directory helper and a simple GitHub Issue conversation. Latency and scale claims need actual measurements before selecting batching, stream rotation, or a more elaborate storage format.

**The strongest synthesis is a small Git-backed collaboration core with optional protocol adapters.**

Borrow durable threading from mail, producer streams from signed-feed systems, collaboration objects from git-bug and Radicle, task vocabulary from current agent protocols, information prerequisites from BSPL, and checkpoint discipline from workflow systems. Use structured artifacts and explicit review policies to turn useful communication into durable commitments.

The next design decisions are concrete: choose the mandatory Git publication profile; specify event identity and ingestion recovery; define a minimal session descriptor; and decide whether the initial task model allows explicit assignment only or also competitive claiming. Those choices can be validated with a few interoperable clients and failure traces before adding a registry, broker, distributed scheduler, or universal agent ontology.
