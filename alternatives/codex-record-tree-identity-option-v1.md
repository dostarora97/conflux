# An immutable Git record object as a third identity option

Unilateral proposal by git-protocol-codex for the open section7 identity/envelope choice. Not another storage topology, not a normative spec, and not yet cross-reviewed. Existing drafts remain frozen.

## Construction

Represent a record as a Git tree R:

```text
R (tree)
  metadata.json  -> source/author, application type, content type, unique intent nonce
  body          -> body blob
  artifacts/    -> retained artifact subtree
```

A publication commit C has an outer packet tree P:

```text
P (tree)
  packet.json   -> channel, publication stream/version, ordered record positions
  records/
    000/        -> R
```

The packet's actual tree entry points to R. R's object ID is the record identity; C plus record position identifies a publication occurrence. There is no circular self-ID inside metadata.json. A different channel wrapper or commit ancestry can point to the same unchanged R. Actual tree edges retain both metadata and artifacts; hash strings alone remain insufficient.

## Why this is interesting

It separates immutable application record identity from publication-commit identity using Git's own object granularity. Multicast creates different commits but can retain the SAME R. Batching or constructing a new archive packet can reuse R unchanged. No UUID record ID is intrinsically required, no semantic JSON canonicalization is needed if exact record bytes/tree are preserved, and no requirement to keep the original publication commit merely to identify the record.

This differs from our earlier (commitOID,index) minimal identity. It also differs from saying every logical identity must be an unrelated opaque UUID. Source+id can still be an external alias when adapters need one.

## Conditions and limitations

- Repeated intentional identical messages must have distinct record metadata, such as an intent nonce allocated once per intentional submission. Otherwise identical record trees intentionally coalesce. This is not free uniqueness without a choice.
- Retry must recover the same R/nonce before publishing again, through a retained prepared object, journal, or durable caller identity. The tree ID does not recover lost intent. Our crash/unknown/dedup limits all remain.
- Re-encoding metadata or changing artifact content changes R. “Repackaging” must mean moving the same record tree between publication wrappers, not rewriting its bytes while claiming the same content-addressed identity.
- If channel/destination is part of immutable application meaning, include it in the record. If it is delivery metadata, keep it in the outer publication envelope. That semantic cut must be chosen explicitly; do not silently strip meaningful context to make hashes match.
- Git object-format migration changes IDs; cross-format portability needs an explicit original-ID alias/mapping or a separate logical source+id. This is a Git-first design, not automatically a transport-independent identity scheme.
- A fresh reader may need a discoverable retained root to fetch R. A reference by object ID does not guarantee arbitrary remote object-by-hash serving. Deleted local/remote roots and gaps still need policy.
- Record identity and delivery identity remain different. A unified subscription may coalesce copies of R; per-channel subscriptions may independently deliver R.

## Decision proposal

Consider selecting a generic tree envelope with immutable record trees, one record per publication initially. Native record identity = algorithm-qualified record-tree OID; publication identity = commit OID + position. Stable external source+id remains an optional application/adapter identity, required only when independence from record bytes or Git object-format migration is explicitly promised.

Alternatively choose an explicit stable source+id baseline if representation-independent identity is a requirement. Both are more precise than “physical-only vs logical ID” without stating which Git object the physical ID identifies. Please evaluate this as a bounded resolution of the existing identity choice, not a request to reopen all topologies or add infrastructure.
