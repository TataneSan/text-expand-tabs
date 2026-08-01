# text-expand-tabs

Convert between tabs and spaces, both directions, with correct column
accounting. Pure Python standard library, zero dependencies - a portable
`expand`/`unexpand`.

## Features

- Tab expansion honours column position (tab = advance to next multiple
  of the tab size)
- `--unexpand` converts leading spaces back to tabs
- Configurable tab size (`-n`, default 8)
- `--check` CI lint mode: exit 2 when the file does not conform
- Reads a file or standard input

## Installation

```bash
pip install .
# or
pip install git+https://github.com/TataneSan/text-expand-tabs.git
```

## Usage

```bash
text-expand-tabs -n 4 source.py
text-expand-tabs --unexpand -n 4 Makefile
text-expand-tabs --check -n 2 file.py   # CI: fail if file uses tabs
printf 'a\tb\n' | text-expand-tabs -n 4
```

### Example

```bash
$ printf 'a\tb\n' | text-expand-tabs -n 4 | cat -A
a   b$
$ printf '    x\n' | text-expand-tabs --unexpand -n 4 | cat -A
^Ix$
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | success (or conforming input with `--check`) |
| 1 | I/O or CLI error |
| 2 | `--check`: conversion would change the input |

## License

MIT
