import sqlite3
import datetime
from typing import List, Dict, Optional, Any

DEFAULT_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS devices (
    mac TEXT PRIMARY KEY,
    ip TEXT,
    vendor TEXT,
    first_seen TEXT,
    last_seen TEXT,
    is_new INTEGER DEFAULT 1,
    trusted INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scanned_at TEXT,
    duration_seconds REAL,
    scanned_count INTEGER
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT,
    mac TEXT,
    note TEXT,
    created_at TEXT
);
"""

def utc_now() -> str:
    """Returns current time as an ISO 8601 UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str) -> None:
    """Initialize database file and tables."""
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        cur.executescript(DEFAULT_SCHEMA)
        conn.commit()
    finally:
        conn.close()

def insert_or_update_device(db_path: str, ip: str, mac: str, vendor: str, first_seen: Optional[str]=None, last_seen: Optional[str]=None) -> None:
    """
    Insert device if new; otherwise update ip/vendor/last_seen.
    Ensures first_seen is set on first insert.
    """
    now = last_seen or utc_now()
    first_seen = first_seen or now

    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        # Try update first (idempotent)
        cur.execute(
            "UPDATE devices SET ip = ?, vendor = ?, last_seen = ?, is_new = 0 WHERE mac = ?",
            (ip, vendor, now, mac)
        )
        if cur.rowcount == 0:
            # Insert new device
            cur.execute(
                "INSERT OR REPLACE INTO devices (mac, ip, vendor, first_seen, last_seen, is_new) VALUES (?, ?, ?, ?, ?, ?)",
                (mac, ip, vendor, first_seen, now, 1)
            )
        conn.commit()
    finally:
        conn.close()

def device_exists(db_path: str, mac: str) -> bool:
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM devices WHERE mac = ? LIMIT 1", (mac,))
        row = cur.fetchone()
        return row is not None
    finally:
        conn.close()

def get_all_devices(db_path: str) -> List[Dict[str, Any]]:
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT mac, ip, vendor, first_seen, last_seen, is_new, trusted, notes FROM devices ORDER BY last_seen DESC")
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def mark_device_seen(db_path: str, mac: str, ip: str, vendor: str, seen_at: Optional[str]=None):
    """
    Convenience wrapper to update/insert when a scan finds a device.
    """
    seen_at = seen_at or utc_now()
    insert_or_update_device(db_path, ip=ip, mac=mac, vendor=vendor, last_seen=seen_at)

def log_scan(db_path: str, duration_seconds: float, scanned_count: int, scanned_at: Optional[str]=None) -> None:
    scanned_at = scanned_at or utc_now()
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scans (scanned_at, duration_seconds, scanned_count) VALUES (?, ?, ?)",
            (scanned_at, duration_seconds, scanned_count)
        )
        conn.commit()
    finally:
        conn.close()

def create_alert(db_path: str, alert_type: str, mac: Optional[str], note: str, created_at: Optional[str]=None) -> None:
    created_at = created_at or utc_now()
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alerts (alert_type, mac, note, created_at) VALUES (?, ?, ?, ?)",
            (alert_type, mac, note, created_at)
        )
        conn.commit()
    finally:
        conn.close()

def get_alerts(db_path: str, limit: int = 100) -> List[Dict[str, Any]]:
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, alert_type, mac, note, created_at FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()