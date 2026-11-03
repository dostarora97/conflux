#!/usr/bin/env python3
"""Isolated Git semantics experiments; no external remotes or user repos."""

import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import tempfile


ENV = dict(os.environ)
ENV.update({
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_AUTHOR_NAME": "Experiment",
    "GIT_AUTHOR_EMAIL": "experiment@example.invalid",
    "GIT_COMMITTER_NAME": "Experiment",
    "GIT_COMMITTER_EMAIL": "experiment@example.invalid",
    "GIT_NO_REPLACE_OBJECTS": "1",
})


def git(repo, *args, input=None, ok=True, date=None):
    env = dict(ENV)
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    result = subprocess.run(
        ["git", "-C", str(repo), "-c", "gc.auto=0", "-c", "pack.threads=1", "-c", "index.threads=1", *args],
        input=input, text=True, capture_output=True, env=env,
    )
    if ok and result.returncode:
        raise RuntimeError(f"git {args!r}: {result.stderr}")
    return result


def init(path):
    path.mkdir()
    git(path, "init", "--bare", "-q")
    return path


def packet(repo, label, parents=(), date=None, body="", refs=()):
    doc = json.dumps({"id": label, "body": body, "refs": list(refs)}, sort_keys=True)
    blob = git(repo, "hash-object", "-w", "--stdin", input=doc).stdout.strip()
    tree = git(repo, "mktree", input=f"100644 blob {blob}\tpacket.json\n").stdout.strip()
    args = ["commit-tree", tree]
    for parent in parents:
        args.extend(["-p", parent])
    oid = git(repo, *args, input=f"{label}\n", date=date).stdout.strip()
    return oid, blob


def has(repo, oid):
    return git(repo, "cat-file", "-e", oid, ok=False).returncode == 0


def run():
    report = {"git_version": subprocess.check_output(["git", "--version"], text=True).strip()}
    with tempfile.TemporaryDirectory(prefix="git-collaboration-", dir="/private/tmp") as tmp:
        base = Path(tmp)
        source = init(base / "source.git")
        remote = init(base / "remote.git")
        url = remote.as_uri()

        # 100 independently named producer streams; parallel pushes, no shared ref.
        streams = []
        for i in range(100):
            oid, _ = packet(source, f"producer-{i}-batch-1", body="hello")
            group = "alpha" if i < 60 else "beta"
            ref = f"refs/collab/v1/rooms/{group}/writers/p{i:03}/head"
            streams.append((oid, ref))
        def publish(pair):
            oid, ref = pair
            result = git(source, "push", "-q", url, f"{oid}:{ref}", ok=False)
            return result.returncode, result.stderr
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(publish, streams))
        codes = [code for code, stderr in results]
        assert codes == [0] * 100, [stderr for code, stderr in results if code]
        report["independent_streams"] = {"writers": 100, "successful_pushes": sum(c == 0 for c in codes)}

        # Same-head competing publications to one ordinary branch.
        root, _ = packet(source, "shared-root")
        git(source, "push", "-q", url, f"{root}:refs/heads/shared")
        siblings = [packet(source, f"contender-{i}", parents=[root])[0] for i in range(16)]
        def contend(oid):
            return git(source, "push", "-q", url, f"{oid}:refs/heads/shared", ok=False).returncode
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            codes = list(executor.map(contend, siblings))
        assert sum(c == 0 for c in codes) == 1
        report["shared_branch"] = {"same_base_candidates": 16, "accepted_without_retry": 1, "rejected": 15}

        # Fetch only alpha. Use fetch into an empty repo, not a local clone that may hardlink objects.
        reader = init(base / "alpha-reader.git")
        git(reader, "fetch", "-q", "--no-tags", url,
            "refs/collab/v1/rooms/alpha/*:refs/seen/alpha/*")
        alpha = sum(has(reader, oid) for oid, ref in streams if "/alpha/" in ref)
        beta = sum(has(reader, oid) for oid, ref in streams if "/beta/" in ref)
        assert (alpha, beta) == (60, 0)
        report["group_fetch"] = {"alpha_commits_present": alpha, "unrelated_beta_commits_present": beta}

        # A Git parent is a transport dependency; an opaque object ID in JSON is not.
        foreign, _ = packet(source, "unrelated-history", body="group beta")
        linked, _ = packet(source, "alpha-linked", parents=[foreign])
        opaque, _ = packet(source, "alpha-opaque", refs=[foreign])
        git(source, "push", "-q", url, f"{linked}:refs/heads/linked", f"{opaque}:refs/heads/opaque")
        linked_reader = init(base / "linked-reader.git")
        opaque_reader = init(base / "opaque-reader.git")
        git(linked_reader, "fetch", "-q", "--no-tags", url, "refs/heads/linked:refs/seen/head")
        git(opaque_reader, "fetch", "-q", "--no-tags", url, "refs/heads/opaque:refs/seen/head")
        assert has(linked_reader, foreign) and not has(opaque_reader, foreign)
        report["dependency_closure"] = {"parent_imports_history": True, "json_reference_imports_history": False}

        # A slow consumer can use ancestry despite the publisher's timestamps moving backwards.
        c1, _ = packet(source, "clock-1", date="2030-01-01T00:00:00Z")
        c2, _ = packet(source, "clock-2", parents=[c1], date="2020-01-01T00:00:00Z")
        c3, _ = packet(source, "clock-3", parents=[c2], date="2010-01-01T00:00:00Z")
        delta = git(source, "rev-list", "--reverse", "--topo-order", f"{c1}..{c3}").stdout.split()
        assert delta == [c2, c3]
        report["ancestry_cursor"] = {"unread_commits_recovered": len(delta), "clock_skew_affects_result": False}

        # Slash prefixes do not imply branch inheritance, and a ref cannot be both leaf and prefix.
        git(source, "update-ref", "refs/heads/engineering", root)
        collision = git(source, "update-ref", "refs/heads/engineering/backend", root, ok=False)
        assert collision.returncode != 0
        report["ref_prefix_collision"] = {"parent_leaf_and_child_ref_can_coexist": False}

        # Atomic push rolls back the otherwise valid update if a different ref's update hook rejects.
        update = remote / "hooks" / "update"
        update.write_text('#!/bin/sh\nif [ "$1" = refs/heads/blocked ]; then exit 1; fi\nexit 0\n')
        update.chmod(0o755)
        atomic = git(source, "push", "--atomic", "-q", url,
                     f"{root}:refs/heads/atomic-valid", f"{root}:refs/heads/blocked", ok=False)
        assert atomic.returncode != 0
        assert git(remote, "show-ref", "--verify", "refs/heads/atomic-valid", ok=False).returncode != 0
        report["atomic_push"] = {"otherwise_valid_ref_published_when_peer_ref_rejected": False}

        # A receive-side append rule remains effective when the client asks for force.
        pre_receive = remote / "hooks" / "pre-receive"
        pre_receive.write_text(
            '#!/bin/sh\n'
            'while read old new ref; do\n'
            '  case "$ref" in refs/collab/*)\n'
            '    case "$new" in 0000000000000000000000000000000000000000) exit 1;; esac\n'
            '    case "$old" in 0000000000000000000000000000000000000000) continue;; esac\n'
            '    git merge-base --is-ancestor "$old" "$new" || exit 1\n'
            '  ;; esac\n'
            'done\nexit 0\n'
        )
        pre_receive.chmod(0o755)
        original, original_ref = streams[0]
        forced = git(source, "push", "--force", "-q", url, f"{root}:{original_ref}", ok=False)
        assert forced.returncode != 0
        assert git(remote, "rev-parse", original_ref).stdout.strip() == original
        report["receive_enforcement"] = {"forced_history_replacement_rejected": True}

        # Custom raw headers are preserved as object bytes. Trailers are separately parseable metadata.
        tree = git(source, "rev-parse", f"{root}^{{tree}}").stdout.strip()
        raw = (f"tree {tree}\nauthor Example <example@example.invalid> 1700000000 +0000\n"
               "committer Example <example@example.invalid> 1700000000 +0000\n"
               "collab-channel alpha\n\nPublish record\n\nCollab-Channel: alpha\n")
        custom = git(source, "hash-object", "-w", "-t", "commit", "--stdin", input=raw).stdout.strip()
        git(source, "push", "-q", url, f"{custom}:refs/heads/custom-metadata")
        metadata_reader = init(base / "metadata-reader.git")
        git(metadata_reader, "fetch", "-q", "--no-tags", url,
            "refs/heads/custom-metadata:refs/seen/head")
        read_raw = git(metadata_reader, "cat-file", "commit", custom).stdout
        trailers = git(source, "interpret-trailers", "--parse", input=raw.split("\n\n", 1)[1]).stdout
        assert read_raw == raw and "Collab-Channel: alpha" in trailers
        report["commit_metadata"] = {"custom_header_survives_git_transfer": True,
                                    "standard_trailer_parser_reads_channel": True,
                                    "porcelain_rewrite_preservation_tested": False}

        # Neither a tombstone snapshot nor deleting a ref erases objects immediately.
        retention = init(base / "retention.git")
        old, old_blob = packet(retention, "old-record-to-delete", body="retained history")
        tombstone, _ = packet(retention, "redaction-record", parents=[old], refs=[old])
        git(retention, "update-ref", "refs/heads/room", tombstone)
        git(retention, "gc", "--prune=now")
        assert has(retention, old_blob)
        git(retention, "update-ref", "-d", "refs/heads/room")
        before_gc = has(retention, old_blob)
        git(retention, "reflog", "expire", "--expire=now", "--all")
        git(retention, "gc", "--prune=now")
        after_gc = has(retention, old_blob)
        assert before_gc and not after_gc
        report["retention"] = {"tombstone_retains_ancestor_payload": True,
                               "ref_deletion_immediately_erases_payload": False,
                               "payload_present_after_all_roots_removed_and_gc": after_gc}

        # Epoch rotation changes reachability without pretending a new root is a fast-forward.
        epoch1, _ = packet(source, "epoch-1", body="older retained record")
        epoch2, _ = packet(source, "epoch-2", body="fresh epoch, older history is optional")
        git(source, "push", "-q", url, f"{epoch1}:refs/collab/epochs/one/head",
            f"{epoch2}:refs/collab/epochs/two/head")
        recent = init(base / "recent-reader.git")
        git(recent, "fetch", "-q", "--no-tags", url, "refs/collab/epochs/two/head:refs/seen/head")
        assert has(recent, epoch2) and not has(recent, epoch1)
        report["epoch_rotation"] = {"new_epoch_fetch_requires_old_epoch": False}

        report["scope"] = "Local semantic checks only; not a throughput benchmark or multi-host deployment test."
    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
