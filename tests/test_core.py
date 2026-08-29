"""Tests for the placeholder module — replace alongside it."""

from mvp_template.core import healthcheck


def test_healthcheck_reports_ok() -> None:
    assert healthcheck() == {"status": "ok"}
