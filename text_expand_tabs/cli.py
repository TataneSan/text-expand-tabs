#!/usr/bin/env python3
"""Expand tab characters into spaces with configurable tab stops.

Expansion is column-aware: each tab advances to the next multiple of
--tabstop from the start of the visual line. Tabs found beyond position 0
are handled like the POSIX expand(1) utility.

Exit codes:
    0  success
    1  I/O or CLI error
    2  --check mode: input still contains tab characters
"""

from __future__ import annotations

import argparse
import json
import sys


def expand_line(line, tabstop):
    out = []
    col = 0
    for ch in line:
        if ch == "\t":
            n = tabstop - (col % tabstop)
            out.append(" " * n)
            col += n
        else:
            out.append(ch)
            col += 1
    return "".join(out)


def process(lines, tabstop):
    out_lines = []
    tabs_total = 0
    lines_had_tabs = 0
    for line in lines:
        stripped_nl = line.rstrip("\n")
        n_tabs = stripped_nl.count("\t")
        if n_tabs:
            tabs_total += n_tabs
            lines_had_tabs += 1
        had_nl = line.endswith("\n")
        expanded = expand_line(stripped_nl, tabstop)
        out_lines.append(expanded + ("\n" if had_nl else ""))
    return out_lines, tabs_total, lines_had_tabs


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="text-expand-tabs",
        description="Expand tab characters into spaces with configurable tab stops.",
    )
    p.add_argument("file", nargs="?", default="-",
                   help="Text file to read (default: stdin; use '-' for stdin)")
    p.add_argument("--tabstop", type=int, default=8,
                   help="Tab stop width in columns (default: 8, like POSIX expand)")
    p.add_argument("--in-place", action="store_true",
                   help="Rewrite the file in place (ignored for stdin)")
    p.add_argument("--check", action="store_true",
                   help="CI mode: do not write output, exit 2 if tabs remain")
    p.add_argument("--json", action="store_true",
                   help="Emit a machine-readable JSON report (on stderr after output)")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress the summary line")
    args = p.parse_args(argv)

    if args.tabstop < 1:
        print("error: --tabstop must be >= 1", file=sys.stderr)
        return 1

    src = args.file
    if src == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(src, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"error: cannot open {src}: {exc}", file=sys.stderr)
            return 1

    lines = text.splitlines(keepends=True)
    out_lines, tabs_total, lines_had_tabs = process(lines, args.tabstop)
    new_text = "".join(out_lines)

    if not args.check:
        if args.in_place and src != "-":
            try:
                with open(src, "w", encoding="utf-8") as fh:
                    fh.write(new_text)
            except OSError as exc:
                print(f"error: cannot write {src}: {exc}", file=sys.stderr)
                return 1
        else:
            sys.stdout.write(new_text)

    report = {
        "file": src,
        "in_place": bool(args.in_place and src != "-"),
        "tabstop": args.tabstop,
        "lines": len(lines),
        "lines_with_tabs": lines_had_tabs,
        "tabs_expanded": tabs_total,
    }
    if args.json:
        print(json.dumps(report), file=sys.stderr)
    elif not args.quiet:
        print(f"{tabs_total} tab(s) expanded on {lines_had_tabs} line(s) "
              f"(tabstop={args.tabstop})", file=sys.stderr)

    if args.check:
        return 2 if tabs_total else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
