# Cluster 02 — Source Modules, Runtime Surface & Test Verification

Code-level audit of implemented modules, CLI/service entrypoints, and automated tests in `project-template-mvp-basic` at `be3c58bc8`.

---

## 101-docs-conf-py — Python Module Group `docs/conf.py`

**Status:** Shipped (`1` tracked file(s) verified on trunk) · **Persona:** Developer

**What it is.** Live Python implementation under `docs/conf.py` (`docs/conf.py`). Contains `1` Python module(s).

---

## 102-src-mvp-template — Python Module Group `src/mvp_template`

**Status:** Shipped (`2` tracked file(s) verified on trunk) · **Persona:** Developer

**What it is.** Live Python implementation under `src/mvp_template` (`src/mvp_template/__init__.py`, `src/mvp_template/core.py`). Key symbols: `healthcheck`.

---

## 103-automation-tooling — Automation Scripts, Hardware & Frontend Assets

**Status:** Shipped (`1` tracked file(s)) · **Persona:** Operator

**What it is.** Repository automation, build scripts, and domain assets: `scripts/ci-local.sh`.

---

## 104-test-verification — Automated Test & Quality Gate Suite

**Status:** Shipped (`1` test file(s) tracked in git) · **Persona:** QA / CI Pipeline

**What it is.** Verification and regression test suite covering `project-template-mvp-basic` invariants (`tests/test_core.py`).
