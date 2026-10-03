"""Fixtures shared by every test."""

from __future__ import annotations

import socket

import pytest


class NetworkBlocked(OSError):
    """Raised by any socket use while :func:`no_network` is active."""


@pytest.fixture
def no_network(monkeypatch):
    """Make every socket creation, connection and DNS lookup fail.

    Use it to prove a code path works offline, and to keep tests that must
    never reach a live service from doing so by accident.
    """

    def refuse(*_args, **_kwargs):
        raise NetworkBlocked("network access is blocked in this test")

    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
