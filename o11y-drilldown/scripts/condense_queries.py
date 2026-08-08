#!/usr/bin/env python3
"""Condense an Axiom queryDataset CSV dump of Spark MCP calls into readable lines.

The Axiom MCP tool writes large results to a file under tool-results/. That file is CSV
with a JSON contexture tree in the `query` column, one call per row. Reading it directly
burns context and hides the fields that matter.

Usage:
    condense_queries.py <dump-file>
        One header line and one rendered tree per call.

    condense_queries.py <dump-file> --raw HH:MM:SS [HH:MM:SS ...]
        Full pretty-printed JSON for the named calls. Use this to diff a pair.
        The rendered view drops fields; the diff must run against the raw JSON.

    condense_queries.py <dump-file> --zero
        Only the calls that gave an empty result or failed.
"""

import csv
import json
import sys

csv.field_size_limit(10**9)


def render(node):
    """One line per filter node. Drops the results node, keeps every flag that changes matching."""
    t = node.get("type")
    k = node.get("key")

    if t == "group":
        parts = [render(c) for c in node.get("children", [])]
        return f"[{node.get('join')}] " + " ; ".join(p for p in parts if p)

    if t == "tagsQuery":
        words = "|".join(str(tag.get("word")) for tag in node.get("tags", []))
        # exact and filterOnly both change what matches; never hide them.
        flags = [f"join={node.get('join')}"]
        if node.get("exact") is not None:
            flags.append(f"exact={node.get('exact')}")
        if node.get("filterOnly"):
            flags.append("filterOnly")
        return f"{k}:tags({node.get('field')})=[{words}] " + ",".join(flags)

    if t == "date":
        span = ""
        if node.get("range") == "exact":
            span = f" {node.get('from')}..{node.get('to')}"
        return f"{k}:date({node.get('field')})={node.get('range')}{span}"

    if t == "facet":
        return f"{k}:facet({node.get('field')})={node.get('values')} mode={node.get('mode')}"

    if t == "number":
        return f"{k}:num({node.get('field')})={node.get('min')}..{node.get('max')}"

    if t == "fieldValuesGroupStats":
        return f"{k}:agg({node.get('groupField')} over {node.get('statsField')})"

    if t == "results":
        return None

    return f"{k}:{json.dumps({a: b for a, b in node.items() if a != 'key'}, separators=(',', ':'))}"


def page_size(node):
    for child in node.get("children", []):
        if child.get("type") == "results":
            return child.get("pageSize")
    return None


def load(path):
    lines = open(path).read().split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("_time,"))
    return [r for r in csv.DictReader(lines[start:]) if r.get("_time")]


def outcome(row):
    if row.get("error_type"):
        return f"FAIL {row['error_type']}"
    if row.get("zero_results") == "true":
        return "ZERO"
    return f"ok r={row.get('records')}/{row.get('returned_records')}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    path = sys.argv[1]
    flags = sys.argv[2:]
    rows = load(path)

    if "--raw" in flags:
        wanted = set(flags[flags.index("--raw") + 1:])
        for row in rows:
            if row["_time"][11:19] in wanted:
                print(f"===== {row['_time'][11:19]} {row['tool']} {outcome(row)}")
                print(json.dumps(json.loads(row["query"]), indent=1, sort_keys=True))
        return 0

    only_zero = "--zero" in flags
    shown = 0
    for n, row in enumerate(rows, 1):
        result = outcome(row)
        if only_zero and result.startswith("ok"):
            continue
        shown += 1
        raw = row.get("query") or ""
        try:
            tree = json.loads(raw)
            body = render(tree)
            meta = f"[{tree.get('schema')}] page={page_size(tree)}"
        except Exception as exc:
            body = f"<unparsed: {exc}> {raw[:200]}"
            meta = "[?]"
        print(f"{n:3d} {row['_time'][:10]} {row['_time'][11:19]} {row['user_email']} "
              f"{row['tool']} {meta} {result}")
        print(f"      {body}")

    print(f"# {shown} shown of {len(rows)} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
