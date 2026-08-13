#!/usr/bin/env python3
"""Summarize ast-grep JSON output.

Reads ast-grep --json output from stdin. Prints match counts per file
and a compact list of matches (file:line + matched text, truncated).

Usage:
    ast-grep -p '<pattern>' --json=compact <path> | python3 json-summary.py
    ast-grep scan --json=stream <path> | python3 json-summary.py --files-only

Works with --json / --json=pretty / --json=compact (one array) and
--json=stream (one object per line). Stream input is parsed line by
line; only the fields needed for the summary are kept in memory.

Note: in a pipeline the shell reports THIS script's exit status, not
ast-grep's. Use `set -o pipefail` when the ast-grep status matters.
"""
import argparse
import json
import sys
from collections import Counter


def fail(msg):
    print(f"json-summary: error: {msg}", file=sys.stderr)
    sys.exit(2)


def slim(match):
    """Keep only the fields the summary needs."""
    if not isinstance(match, dict):
        fail(f"expected a JSON object per match, got {type(match).__name__}")
    return (
        match.get("file", "<stdin>"),
        match.get("range", {}).get("start", {}).get("line", 0) + 1,
        " ".join(match.get("text", "").split()),
        match.get("ruleId", ""),
    )


def read_matches(stream):
    first = ""
    for ch in iter(lambda: stream.read(1), ""):
        if not ch.isspace():
            first = ch
            break
    if not first:
        return []
    rest = stream.read()
    try:
        if first == "[":
            data = json.loads(first + rest)
            if not isinstance(data, list):
                fail("top-level JSON is not an array")
            return [slim(m) for m in data]
        # stream style: one JSON object per line
        return [
            slim(json.loads(line))
            for line in (first + rest).splitlines()
            if line.strip()
        ]
    except json.JSONDecodeError as e:
        fail(f"input is not valid ast-grep JSON ({e}). Did you use --json=compact or --json=stream?")


def plural(n, singular, plural_form=None):
    return f"{n} {singular}" if n == 1 else f"{n} {plural_form or singular + 's'}"


def main():
    parser = argparse.ArgumentParser(description="Summarize ast-grep --json output from stdin.")
    parser.add_argument("--files-only", action="store_true", help="print only the per-file counts")
    parser.add_argument("--max-text", type=int, default=80, metavar="N",
                        help="truncate matched text to N characters (min 10, default 80)")
    args = parser.parse_args()
    if args.max_text < 10:
        parser.error("--max-text must be 10 or greater")

    matches = read_matches(sys.stdin)
    if not matches:
        print("0 matches.")
        return

    per_file = Counter(f for f, _, _, _ in matches)

    print(f"{plural(len(matches), 'match', 'matches')} in {plural(len(per_file), 'file')}\n")
    print("Matches per file:")
    for f, n in per_file.most_common():
        print(f"  {n:5d}  {f}")

    if args.files_only:
        return

    print("\nMatches:")
    for f, line, text, rule in matches:
        if len(text) > args.max_text:
            text = text[: args.max_text - 1] + "…"
        prefix = f"[{rule}] " if rule else ""
        print(f"  {f}:{line}  {prefix}{text}")


if __name__ == "__main__":
    main()
