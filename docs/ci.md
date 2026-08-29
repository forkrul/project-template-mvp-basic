# CI

One set of checks, defined once in the `Makefile` (`make check` = lint + test +
docs), runnable four ways.

## Hosted Woodpecker (forkrul-woodpecker-CI)

The `.woodpecker/` directory holds three lanes, ready for the estate's
[forkrul-woodpecker-CI](https://github.com/forkrul/forkrul-woodpecker-CI)
server:

| Lane | Steps | Delegates to |
|---|---|---|
| `test.yml` | install → lint → test | `make install` / `make lint` / `make test` |
| `security.yml` | gitleaks (working tree) + shellcheck | — (self-contained) |
| `docs.yml` | Sphinx build, zero warnings | `make docs` |

`test.yml` and `security.yml` are **byte-for-byte the estate's `python-uv` and
`security` stack templates** — do not edit them locally; a fleet upgrade
overwrites divergence. Their headers explain the two rules that look like
typos: `$${VAR}` in `commands:` is double-dollar (Woodpecker interpolates the
YAML first), while `${VAR}` in `volumes:` is single-dollar on purpose (the
values arrive via `exec --env`).

To enable: add the repository in the Woodpecker UI — the server reads
`.woodpecker/` as-is. The README badge comes from
`https://<woodpecker-host>/api/badges/<owner>/<repo>/status.svg`.

### wp-local (pre-commit CI)

The estate's local engine runs these same lanes from git hooks:

```sh
wp-local init --template python-uv   # keeps the committed .woodpecker/ pipelines,
                                     # writes .wp-local.yml, installs hooks
git commit -m "chore: adopt wp-local local CI"
```

`init` never touches an existing `.woodpecker/`, so the committed lanes stay
canonical. Commit the `.wp-local.yml` it writes.

## GitHub Actions

`.github/workflows/ci.yml` runs `make setup`, `make lint`, `make test`,
`make docs` on pushes to `master`/`main` and on pull requests — the same
targets, so the two CI systems cannot disagree about what "green" means.

## Locally, in Docker: `make ci-local`

`scripts/ci-local.sh` executes every `.woodpecker/*.yml` through
`woodpecker-cli exec` — the actual pipeline YAML, the same digest-pinned
images, no server required. It supplies the `WP_LOCAL_*` variables the lanes
interpolate into their `volumes:`, mirroring what the wp-local engine does.

It uses `woodpecker-cli` from your PATH if present (e.g.
`nix shell nixpkgs#woodpecker-cli`), otherwise it falls back to the pinned
official image (override with `WOODPECKER_CLI_IMAGE=...`).

Two caveats, both structural:

- **The shell and the Docker daemon must share a filesystem.** Step containers
  are launched as siblings through the Docker socket, so every bind source is
  resolved by the host daemon. A remote `DOCKER_HOST`, or a dev container whose
  paths the daemon cannot see, breaks the mounts.
- **First run is slow.** The lanes fetch toolchains from the pinned nixpkgs
  into a cache volume; later runs reuse it.
