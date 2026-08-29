# Shared forkrul-* packages

The estate ships reusable **private** packages. Nothing here is wired in by
default: the project initiator picks from this menu and adds only what the
project needs. Delete the rows you did not adopt (or this whole file) when you
work through `TEMPLATE_CHECKLIST.md`.

> The one-line descriptions below are inferred from the package names — the
> source repositories were not readable when this menu was written. Correct
> any that are wrong; the repo links are authoritative.

| Package | What it provides (inferred — verify) | Repository |
|---|---|---|
| `forkrul-auth` | Authentication / authorization (sessions, tokens, users) | <https://github.com/forkrul/forkrul-auth> |
| `forkrul-crud` | Generic CRUD layers over models/repositories | <https://github.com/forkrul/forkrul-crud> |
| `forkrul-tasks` | Background tasks / job queues / scheduling | <https://github.com/forkrul/forkrul-tasks> |
| `forkrul-security` | Security tooling; hosts sub-packages (e.g. `forkrul-sbom` under `packages/`) | <https://github.com/forkrul/forkrul-security> |
| `forkrul-audio-tts` | Text-to-speech / audio generation | <https://github.com/forkrul/forkrul-audio-tts> |
| `forkrul-techvideo` | Technical video generation | <https://github.com/forkrul/forkrul-techvideo> |
| `forkrul-common` | Shared utilities used across the estate | <https://github.com/forkrul/forkrul-common> |
| `forkrul-ai` | AI / LLM helpers and clients | <https://github.com/forkrul/forkrul-ai> |
| `forkrul-fastapi` | FastAPI scaffolding, middleware, and conventions | <https://github.com/forkrul/forkrul-fastapi> |

## How to add one

All repositories are private, so git must be able to authenticate first —
either SSH keys, or HTTPS through a credential helper (`gh auth setup-git`
configures one from your `gh` login). CI needs the same: a read token in the
CI secret store, never in the repo.

### As a uv dependency (default)

```sh
uv add "git+https://github.com/forkrul/forkrul-common.git"        # HTTPS
uv add "git+ssh://git@github.com/forkrul/forkrul-common.git"      # SSH
uv add "git+https://github.com/forkrul/forkrul-common.git" --tag v1.2.0   # pin a tag
```

Some repos host several distributions in one tree — install a sub-package with
`subdirectory`, e.g. `forkrul-sbom` out of `forkrul-security`:

```sh
uv add "forkrul-sbom @ git+https://github.com/forkrul/forkrul-security.git#subdirectory=packages/forkrul-sbom"
```

### As a git submodule (when you need the sources in-tree)

```sh
git submodule add https://github.com/forkrul/forkrul-security.git vendor/forkrul-security
git submodule update --init --recursive
```

Prefer the uv dependency: it is version-pinned through `uv.lock`, needs no
submodule bootstrap in CI, and upgrades with `uv lock --upgrade-package`.
Reach for a submodule only when the project must read or vendor the sources
themselves.
