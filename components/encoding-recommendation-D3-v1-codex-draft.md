# Encoding recommendation — D.3 addendum v1

2026-11-03 UTC. Assembled by git-protocol-codex from both peers' discussion; exact peer approval of this artifact is pending. This proposes an updated recommendation for decision-record v3 §D.3 without editing that record. It does not freeze a wire grammar, select a deployed implementation, or establish capacity. The reviewed representation-independent algorithm and trace contracts remain unchanged.

## Recommended direction

Prefer **separate immutable record identity from publication-occurrence identity** for the first general-purpose profile. Within that model, **an immutable Git record tree carried by a publication commit is our current default recommendation**.

This is a judgment about the desired generic collaboration surface and implementation clarity, not a proof of dominance or a universal minimum. The final interoperable profile still needs explicit requirements, a grammar, resource bounds, host checks and cost evidence. One mandatory encoding should eventually be selected for that profile; this note does not require three parsers or simultaneous implementations.

## What the separation means

A record R retains immutable content and meaning-bearing metadata. A publication commit C carries one or more R objects in a channel/writer stream. An entry identifies the publication occurrence using the stream, C and a packet slot or an equivalently specified coordinate.

For the record-tree construction, record identity is R's algorithm-qualified Git tree OID. Reusing the exact unchanged R in a new wrapper preserves that identity; changing metadata bytes, content or artifacts changes it. Semantic equivalence is not byte identity. Git object-format migration does not automatically preserve these IDs.

A repeated intentional submission must be distinguished under the chosen intent scheme; a retry must recover the same prepared identity/inputs. A nonce is one possible mechanism. Record identity, publication acceptance, subscription delivery and business-effect identity remain different domains.

Routing metadata can belong to the wrapper, but essential semantic context cannot be stripped merely to make hashes match. Forwarding an ambiguous approved utterance does not create an authorization. Source/author declarations and content hashes do not by themselves supply attribution or application authority.

## Why record trees are the current default

- **Straightforward graph roles.** Publication history can remain a conventional single-parent stream chain, while ordinary tree entries retain records and their normal blob/tree artifacts. No extra record-commit versus publication-commit parent classification is needed. This simplifies that part of the validator; it does not eliminate core validation.
- **Broader compatibility with linear-history policies.** GitHub's optional linear-history rule blocks merge commits on targeted branches. A multiple-parent publication codec conflicts with that rule when it is enforced; a single-parent/tree-envelope codec avoids that particular conflict. This is a verified conditional policy fact, not a universal host restriction or an assumption that the user's communication repository has it enabled. [GitHub ruleset rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- **Direct occurrence slots.** Ordered tree paths can identify packet slots, including multiple slots pointing to the same R. The record-commit variant also supports ordered distinct records directly through its parent list; that is not a unique tree advantage. Repeated-R slots in that variant need an explicit occurrence scheme such as a manifest matched to retention parents.
- **Clear placement of retrievable payloads.** Bodies and artifacts can be ordinary blobs under R, with actual retained tree edges. This makes payload/core-metadata separation explicit. Both richer codecs can use blob bodies; no claim that record commits inherently destroy partial-clone deferral is justified.

These are modest structural/compatibility reasons. We have not measured an overall object-count, byte-transfer, CPU, latency or throughput advantage for a fully specified pair of codecs. A textual OID, gitlink or submodule entry is not interchangeable with the normal blob/tree retention edges this recommendation assumes.

## Preserve the alternatives

| Alternative | When to consider it | Explicit costs/limits |
|---|---|---|
| **Compact commit-as-record, E=R** | Simple text/citation publication is enough and unchanged-record rewrapping is unnecessary. | Rebuilding the commit changes its record identity. Citation can preserve an existing original through a retained root. Adding a logical record ID introduces another identity domain rather than leaving E=R unchanged. |
| **Parentless record commit R plus publication wrapper** | Native commit-signature verification/inspection is valuable, or a defined layout shows worthwhile cost benefits, and the host/validator accepts the graph profile. | More commit nodes and protocol graph roles; multiple-parent admission/tooling conditions; shallow closure and packet occurrence/retention consistency need explicit handling. It remains viable, not disproved. |
| **Record tree R plus publication wrapper** | Generic payloads, direct record reuse, artifact retention and clear packet slots are useful enough to justify the envelope. | Tree/blob/metadata objects and a shared validator; exact byte identity is not semantic identity; author-attestation and portability profiles remain separate. |

Ordinary Git cannot globally forbid trees while supporting record commits: those commits also refer to trees. A concrete host policy must be named rather than inventing a generic host-forbids-trees revival condition.

Native author signatures on record commits are a real ergonomic benefit, not a unique ability to authenticate immutable content. A tree-based attestation profile can cover an exact payload-tree OID/bytes under an explicit domain without requiring semantic JSON canonicalization. Its storage, reachability and authority rules still need definition; signing is not mandatory here.

## What remains open before an interoperability cut

Define exact record/packet shapes, required versus optional fields, versioning, ordered-slot rules, identity/intent allocation and retry journals, retained artifact/evidence closure, resource bounds, and host mapping. Specify how source metadata and optional attestations are interpreted. Verify the chosen admission/consistency profile and workload budgets. Retain-all remains the initial recommendation while retirement/fencing is unspecified.

The result is a preferred direction with preserved options, not an implemented protocol or proof that every deployment should choose it. A new counterexample or actual cost evidence can revise the recommendation.
