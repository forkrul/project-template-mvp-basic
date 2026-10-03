"""The no_network fixture really blocks the network."""

from __future__ import annotations

import socket
import urllib.request

import pytest


def test_sockets_dns_and_http_are_refused(no_network):
    for attempt in (
        lambda: socket.socket(),
        lambda: socket.create_connection(("example.com", 443)),
        lambda: socket.getaddrinfo("example.com", 443),
        lambda: urllib.request.urlopen("https://example.com", timeout=1),
    ):
        with pytest.raises(OSError, match="blocked"):
            attempt()
