# forkrul-mvp-template

> Minimal, agent-ready Python/uv service skeleton for the forkrul estate — dual CI
> (Woodpecker + GitHub Actions), local pipeline parity in Docker, Sphinx docs gated at
> zero warnings, and an opt-in menu of shared `forkrul-*` packages.

[![Woodpecker CI](https://woodpecker.example.com/api/badges/forkrul/project-template-mvp-basic/status.svg)](https://woodpecker.example.com/repos/forkrul/project-template-mvp-basic)
[![CI](https://github.com/forkrul/project-template-mvp-basic/actions/workflows/ci.yml/badge.svg)](https://github.com/forkrul/project-template-mvp-basic/actions/workflows/ci.yml)
[![Docs: Sphinx, zero warnings](https://img.shields.io/badge/docs-sphinx%20%C2%B7%200%20warnings-blue)](docs/index.md)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Common Changelog](https://common-changelog.org/badge.svg)](https://common-changelog.org)
[![License: Proprietary](https://img.shields.io/badge/license-proprietary-red)](LICENSE)

## What's inside

| Path | Why it exists |
|---|---|
| `AGENTS.md` (+ `CLAUDE.md` pointer) | One instruction file for 30+ coding agents; Claude Code bridged via import |
| `Makefile` | The CI-agnostic seam: every CI lane calls `make` targets, never raw commands |
| `.woodpecker/` | forkrul-woodpecker-CI lanes (`test`, `security`, `docs`) — byte-compatible with `wp-local` |
| `.github/workflows/ci.yml` | The same `make` targets on GitHub Actions |
| `scripts/ci-local.sh` | `make ci-local`: run the real Woodpecker pipelines locally in Docker |
| `docs/` | Sphinx + myst-parser (Markdown-only) site, built with `-W` — zero warnings or the build fails |
| `src/mvp_template/` + `tests/` | Placeholder package + test so every lane exercises something real |
| `PACKAGES.md` | The shared `forkrul-*` package menu — pick what this project needs |
| `TEMPLATE_CHECKLIST.md` | De-templating checklist; ends with a grep proving no template residue remains |
| `CHANGELOG.md` | [Common Changelog](https://common-changelog.org) — hand-curated, no `Unreleased` section |

## Quick start

```sh
make setup        # install toolchain + locked dependencies (uv)
make check        # lint + test + docs — everything CI runs
make docs-serve   # browse the documentation on :8000
```

## CI — one set of checks, three ways to run it

Every lane delegates to the same `Makefile` targets, so they cannot drift:

1. **Hosted Woodpecker** — enable the repo on the forkrul
   [forkrul-woodpecker-CI](https://github.com/forkrul/forkrul-woodpecker-CI) server; it
   picks up `.woodpecker/` as-is. `wp-local init --template python-uv` onboards the
   pre-commit engine and keeps these pipelines untouched.
2. **GitHub Actions** — `.github/workflows/ci.yml` runs `make lint`, `make test`,
   `make docs` on every push and pull request.
3. **Locally, in Docker** — `make ci-local` executes the actual `.woodpecker/*.yml`
   via `woodpecker-cli exec`. Same YAML, same images, no server needed.

Details, caveats, and the badge wiring: [docs/ci.md](docs/ci.md).

## Shared forkrul-* packages

The estate ships reusable private packages (`forkrul-auth`, `forkrul-crud`,
`forkrul-tasks`, `forkrul-security`, `forkrul-audio-tts`, `forkrul-techvideo`,
`forkrul-common`, `forkrul-ai`, `forkrul-fastapi`). None is wired in by default —
pick what this project needs from the menu in [PACKAGES.md](PACKAGES.md), which has
copy-paste `uv add` / submodule commands for each.

## Documentation

`make docs` builds the Sphinx site into `docs/_build/html/`. Sources are plain
Markdown that GitHub renders as-is: start at [docs/index.md](docs/index.md). The build
runs with `-W --keep-going`; a single warning fails CI.

## Using this template

1. On GitHub choose **Use this template** → create a **private** repository
   (the "Template repository" flag must be enabled once in this repo's settings).
2. Work through [TEMPLATE_CHECKLIST.md](TEMPLATE_CHECKLIST.md) top to bottom. It
   renames everything, wires CI and badges, and ends with a verification grep that
   proves no evidence of the template remains.

## License

Proprietary — all rights reserved. See [LICENSE](LICENSE).
