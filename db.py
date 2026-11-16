"""
Per-user storage for the capstone: wardrobes, color profiles and their photos.

    DATABASE_URL=postgresql://...   → Postgres (what the deployed app uses)
    (unset)                         → SQLite at data/fitfindr.db (local runs)

The SQL below is written once and runs on both — queries use `?` and the
Postgres path swaps it for `%s`. Photos live in the database as compressed
WebP (the browser shrinks them to ~1600px before upload, plus a 320px
thumbnail), which keeps one service, one connection string, and no bucket.

Users are identified by a random per-browser ID (a UUID the page keeps in
localStorage). There is no login: knowing the ID is what grants access, so the
ID is never logged in full and never put in a URL.
"""

import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

import config

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))
SQLITE_PATH = Path(os.getenv("AI201_SQLITE_PATH", config.DATA_DIR / "fitfindr.db"))

# A cap, so one browser can't fill the free database by itself.
MAX_PHOTOS_PER_USER = int(os.getenv("AI201_MAX_PHOTOS", "60"))

_BLOB = "BYTEA" if IS_POSTGRES else "BLOB"
SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        created_at DOUBLE PRECISION NOT NULL
    )""",
    f"""CREATE TABLE IF NOT EXISTS photos (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id),
        kind TEXT NOT NULL,                 -- 'wardrobe' | 'profile'
        mime TEXT NOT NULL,
        size_bytes INTEGER NOT NULL,
        data {_BLOB} NOT NULL,
        thumb {_BLOB},
        created_at DOUBLE PRECISION NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS photos_user ON photos(user_id, kind)",
    """CREATE TABLE IF NOT EXISTS wardrobe_items (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id),
        photo_id TEXT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        colors TEXT NOT NULL,               -- JSON list
        style_tags TEXT NOT NULL,           -- JSON list
        notes TEXT NOT NULL DEFAULT '',
        created_at DOUBLE PRECISION NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS items_user ON wardrobe_items(user_id)",
    """CREATE TABLE IF NOT EXISTS profiles (
        user_id TEXT PRIMARY KEY REFERENCES users(id),
        photo_id TEXT,
        data TEXT NOT NULL,                 -- JSON: analyze_profile() result
        updated_at DOUBLE PRECISION NOT NULL
    )""",
]


class QuotaExceeded(Exception):
    """This user already has MAX_PHOTOS_PER_USER photos."""


# ── connection ───────────────────────────────────────────────────────────────

@contextmanager
def _conn():
    """One connection per request: cheap for SQLite, and safe under any worker."""
    if IS_POSTGRES:
        import psycopg
        conn = psycopg.connect(DATABASE_URL, connect_timeout=10)
    else:
        SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(SQLITE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _q(sql: str) -> str:
    return sql.replace("?", "%s") if IS_POSTGRES else sql


def _exec(conn, sql: str, params=()):
    cur = conn.cursor()
    cur.execute(_q(sql), params)
    return cur


_initialized = False


def init() -> None:
    global _initialized
    if _initialized:
        return
    with _conn() as conn:
        for statement in SCHEMA:
            _exec(conn, statement)
    _initialized = True


def backend() -> str:
    return "postgres" if IS_POSTGRES else "sqlite"


# ── users ────────────────────────────────────────────────────────────────────

def valid_user_id(value: str | None) -> str | None:
    """The canonical UUID string, or None if it isn't one."""
    try:
        return str(uuid.UUID(str(value or "")))
    except ValueError:
        return None


def _ensure_user(conn, user_id: str) -> None:
    _exec(conn, "INSERT INTO users (id, created_at) VALUES (?, ?) ON CONFLICT (id) DO NOTHING",
          (user_id, time.time()))


# ── photos ───────────────────────────────────────────────────────────────────

def save_photo(user_id: str, kind: str, data: bytes, mime: str,
               thumb: bytes | None = None) -> str:
    init()
    photo_id = uuid.uuid4().hex
    with _conn() as conn:
        _ensure_user(conn, user_id)
        count = _exec(conn, "SELECT COUNT(*) FROM photos WHERE user_id = ?",
                      (user_id,)).fetchone()[0]
        if count >= MAX_PHOTOS_PER_USER:
            raise QuotaExceeded(
                f"You've stored {count} photos, the limit is {MAX_PHOTOS_PER_USER}. "
                "Delete some to add more.")
        _exec(conn, """INSERT INTO photos
                (id, user_id, kind, mime, size_bytes, data, thumb, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (photo_id, user_id, kind, mime, len(data), data, thumb, time.time()))
    return photo_id


def get_photo(user_id: str, photo_id: str, thumb: bool = False) -> tuple[bytes, str] | None:
    """(bytes, mime) for one of this user's photos, or None. Never another user's."""
    init()
    column = "COALESCE(thumb, data)" if thumb else "data"
    with _conn() as conn:
        row = _exec(conn, f"SELECT {column}, mime, thumb IS NOT NULL FROM photos "
                          "WHERE id = ? AND user_id = ?", (photo_id, user_id)).fetchone()
    if row is None:
        return None
    data, mime, has_thumb = row
    # Thumbnails are always WebP from the browser; the original keeps its own type.
    return bytes(data), ("image/webp" if thumb and has_thumb else mime)


def list_photos(user_id: str, kind: str = "wardrobe") -> list[dict]:
    init()
    with _conn() as conn:
        rows = _exec(conn, "SELECT id, size_bytes, created_at FROM photos "
                           "WHERE user_id = ? AND kind = ? ORDER BY created_at",
                     (user_id, kind)).fetchall()
    return [{"id": r[0], "size_bytes": r[1], "created_at": r[2]} for r in rows]


def delete_photo(user_id: str, photo_id: str) -> bool:
    """Delete a photo and every wardrobe item scanned from it."""
    init()
    with _conn() as conn:
        _exec(conn, "DELETE FROM wardrobe_items WHERE user_id = ? AND photo_id = ?",
              (user_id, photo_id))
        _exec(conn, "UPDATE profiles SET photo_id = NULL WHERE user_id = ? AND photo_id = ?",
              (user_id, photo_id))
        cur = _exec(conn, "DELETE FROM photos WHERE user_id = ? AND id = ?",
                    (user_id, photo_id))
        return cur.rowcount > 0


# ── wardrobe ─────────────────────────────────────────────────────────────────

def add_items(user_id: str, items: list[dict], photo_id: str | None = None) -> list[dict]:
    """Store items (scan_wardrobe's shape). Returns them with their stored ids."""
    init()
    stored = []
    with _conn() as conn:
        _ensure_user(conn, user_id)
        for item in items:
            item_id = uuid.uuid4().hex[:12]
            _exec(conn, """INSERT INTO wardrobe_items
                    (id, user_id, photo_id, name, category, colors, style_tags, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (item_id, user_id, photo_id, item["name"], item["category"],
                   json.dumps(item.get("colors", [])), json.dumps(item.get("style_tags", [])),
                   item.get("notes") or "", time.time()))
            stored.append({**item, "id": item_id, "photo_id": photo_id})
    return stored


def get_wardrobe(user_id: str) -> dict:
    """The user's wardrobe in the wardrobe_schema.json shape (plus photo_id)."""
    init()
    with _conn() as conn:
        rows = _exec(conn, """SELECT id, photo_id, name, category, colors, style_tags, notes
                              FROM wardrobe_items WHERE user_id = ? ORDER BY created_at""",
                     (user_id,)).fetchall()
    return {"items": [
        {"id": r[0], "photo_id": r[1], "name": r[2], "category": r[3],
         "colors": json.loads(r[4]), "style_tags": json.loads(r[5]), "notes": r[6]}
        for r in rows
    ]}


def delete_item(user_id: str, item_id: str) -> bool:
    init()
    with _conn() as conn:
        cur = _exec(conn, "DELETE FROM wardrobe_items WHERE user_id = ? AND id = ?",
                    (user_id, item_id))
        return cur.rowcount > 0


def clear_wardrobe(user_id: str) -> None:
    """Every wardrobe item and wardrobe photo for this user."""
    init()
    with _conn() as conn:
        _exec(conn, "DELETE FROM wardrobe_items WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM photos WHERE user_id = ? AND kind = 'wardrobe'", (user_id,))


# ── profile ──────────────────────────────────────────────────────────────────

def save_profile(user_id: str, profile: dict, photo_id: str | None = None,
                 keep_photo: bool = False) -> None:
    """
    Replace the user's profile. A new profile photo replaces (and deletes) the
    old one; keep_photo=True is for edits that don't come with a new photo.
    """
    init()
    with _conn() as conn:
        _ensure_user(conn, user_id)
        old = _exec(conn, "SELECT photo_id FROM profiles WHERE user_id = ?",
                    (user_id,)).fetchone()
        old_photo = old[0] if old else None
        if keep_photo:
            photo_id = old_photo
        _exec(conn, """INSERT INTO profiles (user_id, photo_id, data, updated_at)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT (user_id) DO UPDATE SET
                         photo_id = excluded.photo_id, data = excluded.data,
                         updated_at = excluded.updated_at""",
              (user_id, photo_id, json.dumps(profile), time.time()))
        if old_photo and old_photo != photo_id:
            _exec(conn, "DELETE FROM photos WHERE user_id = ? AND id = ?",
                  (user_id, old_photo))


def get_profile(user_id: str) -> dict | None:
    init()
    with _conn() as conn:
        row = _exec(conn, "SELECT data, photo_id FROM profiles WHERE user_id = ?",
                    (user_id,)).fetchone()
    if row is None:
        return None
    return {**json.loads(row[0]), "photo_id": row[1]}


def delete_profile(user_id: str) -> None:
    init()
    with _conn() as conn:
        _exec(conn, "DELETE FROM profiles WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM photos WHERE user_id = ? AND kind = 'profile'", (user_id,))


def delete_user(user_id: str) -> None:
    """Everything this browser ever stored."""
    init()
    with _conn() as conn:
        for table, col in (("wardrobe_items", "user_id"), ("profiles", "user_id"),
                           ("photos", "user_id"), ("users", "id")):
            _exec(conn, f"DELETE FROM {table} WHERE {col} = ?", (user_id,))


def storage_used(user_id: str) -> dict:
    init()
    with _conn() as conn:
        row = _exec(conn, "SELECT COUNT(*), COALESCE(SUM(size_bytes), 0) FROM photos "
                          "WHERE user_id = ?", (user_id,)).fetchone()
    return {"photos": row[0], "bytes": int(row[1]), "max_photos": MAX_PHOTOS_PER_USER}
