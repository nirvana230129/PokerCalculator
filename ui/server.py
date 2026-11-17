"""Localhost page that calls the existing equity functions."""

from __future__ import annotations

import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from analytics import hand_grid, hand_grid_from_preflop
from cards import parse_cards
from equity import EquityResult, calculate_equity, equity_vs_random
from ranges import Range

UI_DIR = Path(__file__).resolve().parent


def result_to_dict(result: EquityResult) -> dict:
    return {
        "equity": result.equity,
        "win": result.win,
        "tie": result.tie,
        "lose": result.lose,
        "samples": result.samples,
        "exact": result.exact,
        "elapsed": result.elapsed,
        "method": "exact" if result.exact else "monte_carlo",
        "history": result.history or [],
    }


def _board_from_payload(payload: dict):
    board_text = payload.get("board", "") or ""
    return parse_cards(board_text) if board_text.strip() else []


def _opponents_from_payload(payload: dict):
    if "opponents" in payload and payload["opponents"] is not None:
        return int(payload["opponents"])
    return None


def compute_equity_payload(payload: dict) -> dict:
    """Run one equity calculation from a JSON request body.

    Raises:
        ValueError: the request is missing cards or names an invalid mode.
        KeyError: a required field is absent.
    """
    hero = parse_cards(payload["hero"])
    board = _board_from_payload(payload)
    mode = payload.get("mode", "auto")
    samples = int(payload.get("samples", 10_000))
    seed = payload.get("seed")
    if seed is not None:
        seed = int(seed)
    opponents = _opponents_from_payload(payload)

    if payload.get("villain"):
        result = calculate_equity(
            hero,
            board,
            [Range(payload["villain"])],
            mode=mode,
            n=samples,
            seed=seed,
        )
    elif opponents is not None:
        result = equity_vs_random(hero, board, opponents, n=samples, seed=seed)
    else:
        raise ValueError("Provide villain or opponents")
    return result_to_dict(result)


def compute_grid_payload(payload: dict) -> dict:
    """Build the 13 by 13 equity grid for the page chart."""
    board = _board_from_payload(payload)
    mode = payload.get("mode", "auto")
    samples = int(payload.get("samples", 500))
    seed = payload.get("seed")
    if seed is not None:
        seed = int(seed)
    opponents = _opponents_from_payload(payload)

    if payload.get("villain"):
        return hand_grid(
            board,
            opp_ranges=[Range(payload["villain"])],
            mode=mode,
            n=samples,
            seed=seed,
        )
    if opponents is not None:
        if not board:
            try:
                return hand_grid_from_preflop(opponents)
            except KeyError:
                pass
        return hand_grid(
            board,
            n_opponents=opponents,
            mode=mode,
            n=samples,
            seed=seed,
        )
    raise ValueError("Provide villain or opponents")


class UIHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            page = (UI_DIR / "index.html").read_bytes()
            self._send(200, page, "text/html; charset=utf-8")
            return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        if path not in ("/api/equity", "/api/grid"):
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            payload = json.loads(raw.decode("utf-8"))
            result = compute_equity_payload(payload) if path == "/api/equity" else compute_grid_payload(payload)
            body = json.dumps(result).encode("utf-8")
            self._send(200, body, "application/json")
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            body = json.dumps({"error": str(exc)}).encode("utf-8")
            self._send(400, body, "application/json")


def serve_ui(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    """Serve the equity page until interrupted."""
    server = ThreadingHTTPServer((host, port), UIHandler)
    url = f"http://{host}:{port}/"
    print(f"Open {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        server.server_close()
