# text-expand-tabs

Expand tab characters into spaces with configurable tab stops, like POSIX
`expand(1)` — column-aware, so each tab advances to the next multiple of
`--tabstop` from the start of the visual line.

## Features

- Column-aware expansion (identical to `expand(1)` semantics)
- Custom `--tabstop` (default: 8)
- `--in-place` file rewriting for lint-clean workflows
- Count of expanded tabs and affected lines in a summary (stderr)
- Reads from a file or stdin (`-`)
- `--check` CI mode: exit code 2 when tabs remain (no output written)
- `--json` machine-readable report on stderr

## Install

```sh
pip install .
# or directly from GitHub
pip install git+https://github.com/TataneSan/text-expand-tabs.git
```

Requires Python >= 3.9, standard library only.

## Usage

```sh
text-expand-tabs code.py
cat code.py | text-expand-tabs -
text-expand-tabs code.py --tabstop 4
text-expand-tabs code.py --in-place
text-expand-tabs code.py --check          # exit 2 if tabs still present
```

## Example

```sh
$ printf 'a\tb\tc\n' | text-expand-tabs - --tabstop 4
a   b   c
3 tab(s) expanded on 1 line(s) (tabstop=4)
```

In-place automation:

```sh
$ find src -name '*.py' -exec text-expand-tabs {} --in-place \;
```

Check mode for pre-commit hooks:

```sh
for f in $(git diff --cached --name-only | grep '\.py$'); do
  text-expand-tabs "$f" --check -q || { echo "tabs detected in $f"; exit 1; }
done
```

## Exit codes

- `0` — success (or, with `--check`, no tab characters found)
- `1` — I/O error (cannot open or write file)
- `2` — `--check` mode: tab characters present in the input

## License

MIT — see [LICENSE](LICENSE).
