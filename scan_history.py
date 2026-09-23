"""
scan_history.py — Lightweight persistent scan history.

Every completed scan (host discovery, port scan, web dir scan) is appended
to a local JSON log (~/.network_scanner/history.json) so users can review
past engagements, re-open results, and track recon progress across
sessions — handy when working through a lab/CTF over multiple days.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

HISTORY_DIR = Path.home() / ".network_scanner"
HISTORY_FILE = HISTORY_DIR / "history.json"
MAX_ENTRIES = 200


def _ensure_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> List[dict]:
    _ensure_dir()
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def add_entry(scan_type: str, target: str, summary: str, meta: Optional[dict] = None) -> None:
    """Append a scan summary to the history log, trimming to MAX_ENTRIES."""
    _ensure_dir()
    entries = load_history()
    entries.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "type": scan_type,       # "Host Discovery" | "Port Scan" | "Web Directory Scan"
        "target": target,
        "summary": summary,      # short human-readable summary, e.g. "12 hosts found"
        "meta": meta or {},
    })
    entries = entries[-MAX_ENTRIES:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except OSError:
        pass  # history is a convenience feature; never let it break a scan


def clear_history() -> None:
    _ensure_dir()
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    except OSError:
        pass
