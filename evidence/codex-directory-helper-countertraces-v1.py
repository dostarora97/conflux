"""Scope-limited countertraces against the unchanged file-chat helper.
Only writes scratch temporary directories; emits JSON. Not a Git implementation test.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile

DENO = "/Users/I533118/.deno/bin/deno"
HELPER = "/Users/I533118/.agents/chats/skills/agent-chat.ts"
T = 1793655000000

def put(s, name, content, stamp):
    p = s / name
    p.write_text(content)
    os.utime(p, ns=(stamp * 1000000, stamp * 1000000))
    return p

def wait(s):
    r = subprocess.run([DENO, "run", "--allow-read", "--allow-write", HELPER,
        "wait", "--session", str(s), "--self", "reader",
        "--state-file", str(s / ".reader.watermark"), "--timeout", "0.03",
        "--max-tries", "1"], text=True, capture_output=True, timeout=10)
    return {"exit": r.returncode, "stdout": r.stdout.splitlines(),
        "watermark": (s / ".reader.watermark").read_text() if (s / ".reader.watermark").exists() else None}

out = {"scope": "unchanged local directory helper, deterministic scratch schedules; not production frequency estimates"}
with tempfile.TemporaryDirectory(prefix="agent-chat-countertrace-") as d:
    s = Path(d)
    p1 = put(s, "001-peer.json", json.dumps({"from": "peer", "msg": "first"}), T)
    first = wait(s)
    p2 = put(s, "002-peer.json", json.dumps({"from": "peer", "msg": "second"}), T)
    second = wait(s)
    assert first["exit"] == 0 and str(p1) in first["stdout"]
    assert second["exit"] == 2 and str(p2) not in second["stdout"]
    out["same_millisecond_after_observation"] = {"first": first, "second": second,
        "late_message_exists": p2.exists(), "observed": "new distinct message omitted because mtime equals saved watermark"}
    p3 = put(s, "003-peer.json", json.dumps({"from": "peer", "msg": "older timestamp"}), T - 1000)
    third = wait(s)
    assert third["exit"] == 2 and str(p3) not in third["stdout"]
    out["backdated_or_preserved_mtime"] = {"result": third,
        "late_message_exists": p3.exists(), "observed": "new distinct message omitted because mtime precedes saved watermark"}
    # No application-level read/ack of p1 occurred between first and subsequent waits.
    out["discovery_not_processing"] = {"observed": "watermark already advances when paths are emitted, before caller reads or processes contents",
        "contract": "safe only if caller persists returned pending paths or separately audits unhandled identities after a crash"}
with tempfile.TemporaryDirectory(prefix="agent-chat-partial-") as d:
    s = Path(d)
    p = put(s, "001-peer.json", "{", T)
    result = wait(s)
    assert result["exit"] == 0 and str(p) in result["stdout"]
    out["incomplete_visible_file"] = {"result": result,
        "observed": "helper emits and checkpoints a visible final-name path without checking complete JSON",
        "contract": "notification of a path is not validated durable ingestion; reader must handle incomplete writes/retry"}
print(json.dumps(out, indent=2))
