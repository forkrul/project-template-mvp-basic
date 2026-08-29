#!/usr/bin/env bash
# Run this repository's .woodpecker/ pipelines locally, in Docker, via
# `woodpecker-cli exec` — the "local docker for Woodpecker". The exact YAML the
# hosted server runs is what runs here; nothing is translated or approximated.
#
# The WP_LOCAL_* variables below replicate what the forkrul-woodpecker-CI
# wp-local engine supplies with `exec --env`: the pipelines interpolate them
# into their `volumes:` (single-`$`, deliberately — see .woodpecker/test.yml).
#
# woodpecker-cli is found in this order:
#   1. On PATH (e.g. `nix shell nixpkgs#woodpecker-cli`) — preferred.
#   2. The pinned official image, run with the repo mounted at its own host
#      path plus the host Docker socket. Identical paths matter: the CLI
#      launches step containers as SIBLINGS through the socket, so every bind
#      source is resolved by the HOST daemon. This is also why a remote
#      DOCKER_HOST cannot work here — see docs/ci.md.
set -euo pipefail

WOODPECKER_CLI_IMAGE="${WOODPECKER_CLI_IMAGE:-docker.io/woodpeckerci/woodpecker-cli:v3.17.0}"

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

if [ ! -d .woodpecker ]; then
    echo "ci-local: no .woodpecker/ directory here" >&2
    exit 1
fi

gitdir="$(git rev-parse --path-format=absolute --git-common-dir)"
state="$gitdir/wp-local-lite"
mkdir -p "$state/mask-empty" "$state/mask-config" "$state/cache-uv" \
    "$state/cache-nix" "$state/artifacts"

env_args=(
    --env "CI=woodpecker"
    --env "WP_LOCAL_GITDIR=$gitdir"
    --env "WP_LOCAL_MASK_EMPTY=$state/mask-empty"
    --env "WP_LOCAL_MASK_CONFIG=$state/mask-config"
    --env "WP_LOCAL_CACHE_UV=$state/cache-uv"
    --env "WP_LOCAL_CACHE_NIX=$state/cache-nix"
    --env "WP_LOCAL_ARTIFACT_DIR=$state/artifacts"
    --env "WP_LOCAL_ARTIFACTS=/woodpecker-artifacts"
)

if command -v woodpecker-cli >/dev/null 2>&1; then
    cli=(woodpecker-cli)
else
    if ! command -v docker >/dev/null 2>&1; then
        echo "ci-local: need woodpecker-cli on PATH or a working docker" >&2
        exit 1
    fi
    cli=(docker run --rm
        -v /var/run/docker.sock:/var/run/docker.sock
        -v "$repo_root:$repo_root" -w "$repo_root"
        "$WOODPECKER_CLI_IMAGE")
fi

status=0
for pipeline in .woodpecker/*.yml; do
    echo "==> $pipeline"
    if "${cli[@]}" exec "${env_args[@]}" "$pipeline"; then
        echo "==> $pipeline: OK"
    else
        echo "==> $pipeline: FAILED" >&2
        status=1
    fi
done

if [ "$status" -eq 0 ]; then
    echo "ci-local: all pipelines green (artifacts: $state/artifacts)"
else
    echo "ci-local: at least one pipeline failed" >&2
fi
exit "$status"
