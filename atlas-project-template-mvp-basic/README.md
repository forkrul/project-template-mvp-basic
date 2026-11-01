# `atlas-project-template-mvp-basic` — Feature & Reality Audit Atlas

> Verified against `origin/master` @ `be3c58bc8` (2026-10-31).

## Summary Counts (via `build.py` Oracle)

- **Total Audited Items**: `15`
- **Shipped**: `15`
- **Backend Only**: `0`
- **Partial**: `0`
- **Spec Only**: `0`

## Domain Clusters

- [Cluster 01 — Architecture, Specifications & Functional Domains](clusters/cluster-01-architecture-and-specs.md) (11 items)
- [Cluster 02 — Source Modules, Runtime Surface & Test Verification](clusters/cluster-02-implementation-and-verification.md) (4 items)

## Artifacts & Regeneration

- **Single-File Consolidated Markdown**: [`atlas.md`](atlas.md)
- **Self-Contained Interactive HTML Atlas**: [`atlas.html`](atlas.html)
- **API Surface**: No HTTP API (`mode: none` — CLI / library / hardware / documentation corpus). See [`live-api-surface.md`](live-api-surface.md) for module and test inventory.

To rebuild `atlas.html` and `atlas.md` from `clusters/*.md`:

```bash
python3 build.py
```
