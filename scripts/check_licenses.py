"""Licence gate: fail the build on copyleft or unknown runtime licences.

Part of ``make check``:

* the runtime set is the transitive closure of this project's ``Requires-Dist``,
  including the extras listed in ``SHIPPED_EXTRAS`` and excluding the others;
* a distribution's licence is read from ``License-Expression``, else
  ``License``, else its ``License ::`` classifiers;
* any text containing ``GPL`` (so also LGPL/AGPL) or ``Affero``, or an unknown
  licence, fails unless the distribution is listed in ``licenses-allow.toml``
  with ``name``, ``reason`` and ``approved_by``.

Usage: ``python scripts/check_licenses.py [--root NAME] [--allowlist PATH]``.
Standard library only.
"""

from __future__ import annotations

import argparse
import importlib.metadata as md
import pathlib
import re
import sys
import tomllib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field

ROOT_DISTRIBUTION = "forkrul-mvp-template"
SHIPPED_EXTRAS: frozenset[str] = frozenset()  # extras that ship at runtime, e.g. {"api"}
DEFAULT_ALLOWLIST = pathlib.Path(__file__).resolve().parents[1] / "licenses-allow.toml"
_REQUIRED_ALLOW_FIELDS = ("name", "reason", "approved_by")
_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
_EXTRA_RE = re.compile(r"""extra\s*==\s*["']([^"']+)["']""")
_COPYLEFT_RE = re.compile(r"gpl|affero", re.IGNORECASE)


@dataclass(frozen=True)
class DistInfo:
    """The slice of a distribution's metadata the gate needs."""

    name: str
    requires: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)


def normalize(name: str) -> str:
    """Return the PEP 503 normalized form of a distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def licence_text(dist: DistInfo) -> str | None:
    """Return the declared licence, in D.9 precedence order, or ``None``."""
    for key in ("License-Expression", "License"):
        value = dist.metadata.get(key)
        if isinstance(value, str) and value.strip() and value.strip().upper() != "UNKNOWN":
            return value.strip()
    classifiers = dist.metadata.get("Classifier") or []
    licences = [c for c in classifiers if isinstance(c, str) and c.startswith("License ::")]
    return "; ".join(licences) if licences else None


def classify(dist: DistInfo, allow: Mapping[str, Mapping[str, str]]) -> tuple[bool, str]:
    """Decide whether *dist* may ship. Returns ``(ok, reason)``."""
    entry = allow.get(normalize(dist.name))
    if entry is not None:
        return True, f"allowlisted: {entry['reason']} (approved by {entry['approved_by']})"
    text = licence_text(dist)
    if text is None:
        return False, "unknown licence"
    if _COPYLEFT_RE.search(text):
        return False, f"copyleft licence: {text}"
    return True, text


def load_allowlist(path: pathlib.Path) -> dict[str, dict[str, str]]:
    """Load ``[[allow]]`` entries keyed by normalized name; every field is required."""
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    entries: dict[str, dict[str, str]] = {}
    for entry in data.get("allow", []):
        missing = [key for key in _REQUIRED_ALLOW_FIELDS if not str(entry.get(key, "")).strip()]
        if missing:
            raise ValueError(f"allowlist entry {entry!r} is missing: {', '.join(missing)}")
        entries[normalize(entry["name"])] = {key: str(entry[key]) for key in _REQUIRED_ALLOW_FIELDS}
    return entries


def _requirement(spec: str, extras: Iterable[str]) -> str | None:
    """Return the requirement's normalized name if it applies, else ``None``."""
    requirement, _, marker = spec.partition(";")
    match = _NAME_RE.match(requirement)
    if match is None:
        return None
    wanted = _EXTRA_RE.findall(marker)
    if wanted and not set(wanted) & set(extras):
        return None
    return normalize(match.group(1))


def runtime_closure(
    root: str,
    lookup: Callable[[str], DistInfo | None],
    extras: Iterable[str] = SHIPPED_EXTRAS,
) -> set[str]:
    """Return the normalized names reachable from *root* (excluding *root* itself).

    Root-level requirements honour *extras*; transitive requirements behind any
    extra marker are skipped. Requirements that are not installed are skipped.
    """
    extras = set(extras)
    seen: set[str] = set()
    root_dist = lookup(root)
    if root_dist is None:
        return seen
    stack = [(spec, extras) for spec in root_dist.requires]
    while stack:
        spec, active = stack.pop()
        name = _requirement(spec, active)
        if name is None or name in seen:
            continue
        dist = lookup(name)
        if dist is None:
            continue
        seen.add(name)
        stack.extend((child, set()) for child in dist.requires)
    return seen


def installed(name: str) -> DistInfo | None:
    """Look up an installed distribution by name."""
    try:
        dist = md.distribution(name)
    except md.PackageNotFoundError:
        return None
    meta = dist.metadata
    metadata: dict[str, object] = {
        key: meta.get(key) for key in ("License-Expression", "License") if meta.get(key)
    }
    metadata["Classifier"] = meta.get_all("Classifier") or []
    return DistInfo(name=meta["Name"], requires=tuple(dist.requires or ()), metadata=metadata)


def main(argv: list[str] | None = None) -> int:
    """Run the gate over the installed runtime closure; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=ROOT_DISTRIBUTION)
    parser.add_argument("--allowlist", type=pathlib.Path, default=DEFAULT_ALLOWLIST)
    args = parser.parse_args(argv)

    allow = load_allowlist(args.allowlist)
    failures = 0
    for name in sorted(runtime_closure(args.root, installed)):
        dist = installed(name)
        assert dist is not None
        ok, reason = classify(dist, allow)
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {dist.name}: {reason}")
    if failures:
        print(f"licence gate: {failures} distribution(s) failed", file=sys.stderr)
        return 1
    print("licence gate: passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
