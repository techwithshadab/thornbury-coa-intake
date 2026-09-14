#!/usr/bin/env python3
"""
Check the SHAPE of a decisions.jsonl file. Nothing else.

    ./validate_submission.py decisions.jsonl documents/

This tells you whether your file can be read: one line per document, a valid action, the
required fields present, dates that mean one thing. It does NOT tell you whether any answer
is right — establishing that is the work, and no tool here will do it for you.

Exit 0 = the file is well-formed. Exit 1 = it is not, and every problem is listed.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = ["lot_id", "material_no", "supplier", "manufacture_date", "retest_date"]


def parse_date(s):
    """Return an unambiguous ISO date, or None.

    Accepted: 2026-01-27 · 2026-01-27T00:00:00 · 27 January 2026 · 01/27/2026
    Rejected: 03/04/2026 — that is 3 April or 4 March, and the reader cannot tell which.

    The rejection is the point. A date that reads two ways has not been normalised; it has
    been passed on.
    """
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None

    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:[T ].*)?$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), m.group(3)
        if a > 12 and b <= 12:
            return f"{y}-{b:02d}-{a:02d}"
        if b > 12 and a <= 12:
            return f"{y}-{a:02d}-{b:02d}"
        return None

    for fmt in ("%d %B %Y", "%d %b %Y", "%B %d %Y", "%b %d %Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(s.replace(",", ""), fmt).date().isoformat()
        except ValueError:
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("decisions", help="your decisions.jsonl")
    ap.add_argument("documents", nargs="?", help="the documents directory, to check coverage")
    args = ap.parse_args()

    problems, warnings = [], []
    seen = {}

    path = Path(args.decisions)
    if not path.exists():
        print(f"{path} does not exist")
        return 1

    for n, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"line {n}: not valid JSON — {e}")
            continue
        if not isinstance(d, dict):
            problems.append(f"line {n}: each line must be a JSON object")
            continue

        doc_id = d.get("doc_id")
        if not doc_id:
            problems.append(f"line {n}: no doc_id")
            continue
        if doc_id in seen:
            problems.append(f"line {n}: doc_id {doc_id} already appeared on line {seen[doc_id]}")
        seen[doc_id] = n

        action = str(d.get("action", "")).strip().lower()
        if action not in ("accept", "hold"):
            problems.append(f"{doc_id}: action is {d.get('action')!r}, must be accept or hold")
            continue

        if action == "hold":
            if not str(d.get("hold_reason") or "").strip():
                problems.append(f"{doc_id}: a hold needs a hold_reason")
            continue

        fields = d.get("fields")
        if not isinstance(fields, dict):
            problems.append(f"{doc_id}: an accept needs a fields object")
            continue

        for k in REQUIRED_FIELDS:
            if k not in fields:
                problems.append(f"{doc_id}: fields is missing {k}")

        for k in ("manufacture_date", "retest_date"):
            v = fields.get(k)
            if v in (None, "", "null"):
                continue  # absent is a claim; the scorer judges it
            if parse_date(v) is None:
                problems.append(
                    f"{doc_id}: {k} {v!r} is ambiguous or unparseable — "
                    f"a reader cannot tell which date you mean"
                )

        tests = fields.get("tests")
        if not isinstance(tests, list) or not tests:
            problems.append(f"{doc_id}: tests must be a non-empty list")
            continue
        for t in tests:
            if not isinstance(t, dict):
                problems.append(f"{doc_id}: every entry in tests must be an object")
                continue
            for k in ("attribute", "result", "unit"):
                if k not in t:
                    problems.append(f"{doc_id}: a test entry is missing {k}")
            if "result" in t:
                try:
                    float(t["result"])
                except (TypeError, ValueError):
                    problems.append(
                        f"{doc_id}: {t.get('attribute')!r} result {t.get('result')!r} is not a number"
                    )

    if args.documents:
        docs = {p.stem for p in Path(args.documents).glob("*.txt")}
        missing = sorted(docs - set(seen))
        extra = sorted(set(seen) - docs)
        if missing:
            problems.append(
                f"no line for {len(missing)} document(s): "
                f"{', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}"
            )
        if extra:
            warnings.append(
                f"{len(extra)} line(s) for documents not in that directory: "
                f"{', '.join(extra[:5])}{'...' if len(extra) > 5 else ''}"
            )

    for w in warnings:
        print(f"note: {w}")
    if problems:
        print(f"\n{len(problems)} problem(s):\n")
        for p in problems:
            print(f"  {p}")
        return 1

    print(f"{len(seen)} decisions, well-formed.")
    print("This says nothing about whether they are correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
