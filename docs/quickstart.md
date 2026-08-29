# Quickstart

## Prerequisites

- [uv](https://github.com/astral-sh/uv) — the only hard requirement; it installs
  the pinned Python and all dependencies.
- Docker — only for `make ci-local` (running the Woodpecker pipelines locally).

## Daily commands

```sh
make setup        # install toolchain + locked dependencies
make check        # lint + test + docs — exactly what CI runs
make format       # reformat and autofix (ruff)
make docs-serve   # build the docs and serve them on :8000
make ci-local     # run the real .woodpecker/ pipelines in Docker
make help         # list every target
```

## Layout

| Path | Purpose |
|---|---|
| `src/mvp_template/` | The package (placeholder — rename per the [template checklist](template-checklist.md)) |
| `tests/` | pytest suite |
| `docs/` | This site: Markdown sources, `conf.py`, built into `docs/_build/html/` |
| `.woodpecker/` | Woodpecker CI lanes: `test.yml`, `security.yml`, `docs.yml` |
| `.github/workflows/ci.yml` | GitHub Actions running the same `make` targets |
| `scripts/ci-local.sh` | The `make ci-local` runner |

## The one rule

Every CI lane delegates to `make` targets. If a check needs to change, change
the Makefile — never the pipeline files — and all four ways of running CI
(hosted Woodpecker, GitHub Actions, `wp-local`, `make ci-local`) change
together.
