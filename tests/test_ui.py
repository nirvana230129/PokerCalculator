import json
from http.client import HTTPConnection
from threading import Thread

import pytest

from ui.server import UIHandler, compute_equity_payload
from http.server import ThreadingHTTPServer


def test_compute_equity_payload_river_aces_beat_kings():
    result = compute_equity_payload(
        {
            "hero": "As Ah",
            "board": "2c 7d 9h 4s 3c",
            "villain": "KK",
            "mode": "exact",
        }
    )
    assert result["equity"] == 1
    assert result["exact"] is True
    assert result["method"] == "exact"
    assert result["win"] == 1


def test_http_equity_endpoint_returns_json():
    server = ThreadingHTTPServer(("127.0.0.1", 0), UIHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        conn = HTTPConnection(host, port, timeout=30)
        body = json.dumps(
            {
                "hero": "As Ah",
                "board": "2c 7d 9h 4s 3c",
                "villain": "KK",
                "mode": "exact",
            }
        )
        conn.request("POST", "/api/equity", body=body, headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode())
        assert response.status == 200
        assert payload["equity"] == 1
        conn.request("GET", "/")
        page = conn.getresponse()
        html = page.read().decode()
        assert page.status == 200
        assert "Texas Hold'em equity" in html
    finally:
        server.shutdown()
        server.server_close()
