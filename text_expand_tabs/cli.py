"""Expand tabs to spaces, or unexpand spaces back to tabs.

By default, tabs are expanded to spaces using the given tab size,
honouring column positions (a tab advances to the next multiple of the
tab size). With --unexpand the reverse is done on leading whitespace
only. With --check, the tool prints nothing and exits 2 when the input
does not already satisfy the requested convention.

Exit codes:
  0 - success (or input already conforms with --check)
  1 - I/O or CLI error
  2 - --check: conversion would change the input
"""

import argparse
import sys


def expand_line(line, size):
    out = []
    col = 0
    for ch in line:
        if ch == "\t":
            spaces = size - (col % size)
            out.append(" " * spaces)
            col += spaces
        else:
            out.append(ch)
            col += 1
    return "".join(out)


def unexpand_line(line, size):
    # only leading whitespace is converted back
    prefix = line[: len(line) - len(line.lstrip(" "))]
    rest = line[len(prefix):]
    out = []
    col = 0
    run = 0
    for _ in prefix:
        run += 1
        col += 1
        if col % size == 0:
            out.append("\t")
            run = 0
    out.append(" " * run)
    return "".join(out) + rest


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="text-expand-tabs",
        description="Convert between tabs and spaces in text.",
    )
    parser.add_argument("file", nargs="?", default="-", help="Input file (default: stdin)")
    parser.add_argument("-n", "--size", type=int, default=8, help="Tab size (default: 8)")
    parser.add_argument("--unexpand", action="store_true",
                        help="Convert leading spaces back to tabs")
    parser.add_argument("--check", action="store_true",
                        help="Exit 2 if the input would be changed (CI lint mode)")
    args = parser.parse_args(argv)

    if args.size < 1:
        print("text-expand-tabs: --size must be >= 1", file=sys.stderr)
        return 1

    try:
        if args.file == "-":
            lines = sys.stdin.readlines()
        else:
            with open(args.file, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
    except OSError as exc:
        print(f"text-expand-tabs: {exc}", file=sys.stderr)
        return 1

    convert = (lambda ln: unexpand_line(ln, args.size)) if args.unexpand else (
        lambda ln: expand_line(ln, args.size)
    )

    changed = 0
    output = []
    for line in lines:
        body = line.rstrip("\n")
        newline = "\n" if line.endswith("\n") else ""
        converted = convert(body)
        if converted != body:
            changed += 1
        output.append(converted + newline)

    if args.check:
        if changed:
            print(f"text-expand-tabs: {changed} line(s) would change", file=sys.stderr)
            return 2
        return 0

    sys.stdout.writelines(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
