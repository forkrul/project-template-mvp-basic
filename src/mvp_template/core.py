"""Core placeholder module.

Replace this module once real code exists. It is here so the lint, test, and
documentation lanes all exercise something genuine from day one.
"""

from __future__ import annotations


def healthcheck() -> dict[str, str]:
    """Return a minimal liveness payload.

    Returns:
        A mapping with a single ``"status"`` key whose value is ``"ok"``.
    """
    return {"status": "ok"}
