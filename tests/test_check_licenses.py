"""Tests for the licence gate (spec FR-039, Appendix D.9)."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

_LGPL_CLASSIFIER = "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
_GPL_CLASSIFIER = "License :: OSI Approved :: GNU General Public License (GPL)"
_SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "check_licenses.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_licenses", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate():
    return _load()


def _dist(gate, name, requires=(), **meta):
    return gate.DistInfo(name=name, requires=tuple(requires), metadata=meta)


def test_permissive_licence_passes(gate):
    ok, _ = gate.classify(_dist(gate, "a", **{"License-Expression": "MIT"}), {})
    assert ok


def test_gpl_licence_fails(gate):
    ok, reason = gate.classify(_dist(gate, "a", License="GPL-3.0-or-later"), {})
    assert not ok
    assert "GPL" in reason


def test_lgpl_licence_fails(gate):
    ok, _ = gate.classify(
        _dist(gate, "a", Classifier=[_LGPL_CLASSIFIER]),
        {},
    )
    assert not ok


def test_affero_licence_fails(gate):
    ok, _ = gate.classify(_dist(gate, "a", License="GNU Affero General Public License v3"), {})
    assert not ok


def test_unknown_licence_fails(gate):
    ok, reason = gate.classify(_dist(gate, "a"), {})
    assert not ok
    assert "unknown" in reason


def test_allowlisted_distribution_passes(gate):
    allow = {"a": {"name": "a", "reason": "MIT per bundled LICENSE", "approved_by": "author"}}
    ok, reason = gate.classify(_dist(gate, "a"), allow)
    assert ok
    assert "allowlisted" in reason


def test_licence_expression_takes_precedence_over_classifiers(gate):
    dist = _dist(
        gate,
        "a",
        **{"License-Expression": "Apache-2.0", "Classifier": [_GPL_CLASSIFIER]},
    )
    ok, _ = gate.classify(dist, {})
    assert ok


def test_allowlist_entries_require_all_fields(gate, tmp_path):
    path = tmp_path / "allow.toml"
    path.write_text('[[allow]]\nname = "a"\nreason = "x"\n')
    with pytest.raises(ValueError, match="approved_by"):
        gate.load_allowlist(path)


def test_closure_follows_requires_and_only_the_api_extra(gate):
    dists = {
        "root": _dist(gate, "root", requires=["a>=1", 'b ; extra == "api"', 'c ; extra == "dev"']),
        "a": _dist(gate, "a", requires=["d"]),
        "b": _dist(gate, "b"),
        "c": _dist(gate, "c"),
        "d": _dist(gate, "d"),
    }
    assert gate.runtime_closure("root", dists.get, extras={"api"}) == {"a", "b", "d"}


def test_closure_skips_requirements_that_are_not_installed(gate):
    dists = {"root": _dist(gate, "root", requires=["missing"])}
    assert gate.runtime_closure("root", dists.get, extras=set()) == set()


def test_real_environment_passes(gate):
    assert gate.main([]) == 0
