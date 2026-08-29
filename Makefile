# Developer entry points. Every CI lane (GitHub Actions, hosted Woodpecker,
# wp-local, `make ci-local`) calls these same targets — change behaviour here,
# not in the pipeline files. That is what keeps the four of them in agreement.

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

.PHONY: help setup install lint format test docs docs-serve check ci-local clean

help:  ## List targets.
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

setup:  ## Install toolchain + dependencies (uv-managed, locked).
	uv sync

install: setup  ## Alias for setup (what the Woodpecker python-uv lane delegates to).

lint:  ## Static checks: ruff lint + format check.
	uv run ruff check .
	uv run ruff format --check .

format:  ## Reformat and autofix.
	uv run ruff format .
	uv run ruff check --fix .

test:  ## Run the test suite.
	uv run pytest

docs:  ## Build the Sphinx site; any warning fails the build.
	uv run sphinx-build -W --keep-going -b html docs docs/_build/html
	@echo "docs: docs/_build/html/index.html"

docs-serve: docs  ## Build the site and serve it on :8000.
	uv run python -m http.server 8000 --directory docs/_build/html

check: lint test docs  ## Everything CI runs.

ci-local:  ## Run the .woodpecker/ pipelines locally in Docker (woodpecker-cli exec).
	bash scripts/ci-local.sh

clean:  ## Remove caches and build output.
	rm -rf docs/_build .pytest_cache .ruff_cache dist
