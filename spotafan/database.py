import sqlite3
import threading
from datetime import datetime

from spotafan.config import Config


class Database:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._conn = sqlite3.connect(
            str(Config.DB_PATH),
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._lock = threading.Lock()
        self._create_tables()

    def _create_tables(self):
        with self._lock:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT DEFAULT 'Unknown Artist',
                    album TEXT DEFAULT 'Unknown Album',
                    duration REAL DEFAULT 0,
                    file_path TEXT UNIQUE NOT NULL,
                    source_url TEXT,
                    source_id TEXT,
                    thumbnail TEXT,
                    downloaded_at TEXT NOT NULL,
                    play_count INTEGER DEFAULT 0,
                    last_played TEXT
                );

                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS playlist_songs (
                    playlist_id INTEGER NOT NULL,
                    song_id INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    PRIMARY KEY (playlist_id, song_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    artist TEXT,
                    source_url TEXT NOT NULL,
                    source_id TEXT,
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0,
                    file_path TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                );
            """)
            self._conn.commit()

    # ---- Song operations ----

    def add_song(self, title, artist, album, duration, file_path,
                 source_url="", source_id="", thumbnail=""):
        now = datetime.now().isoformat()
        with self._lock:
            try:
                cur = self._conn.execute(
                    """INSERT INTO songs
                       (title, artist, album, duration, file_path,
                        source_url, source_id, thumbnail, downloaded_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (title, artist, album, duration, str(file_path),
                     source_url, source_id, thumbnail, now),
                )
                self._conn.commit()
                return cur.lastrowid
            except sqlite3.IntegrityError:
                cur = self._conn.execute(
                    "SELECT id FROM songs WHERE file_path = ?",
                    (str(file_path),),
                )
                row = cur.fetchone()
                return row["id"] if row else None

    def get_all_songs(self):
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM songs ORDER BY downloaded_at DESC"
            )
            return [dict(r) for r in cur.fetchall()]

    def get_song_by_id(self, song_id):
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM songs WHERE id = ?", (song_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def search_songs(self, query):
        with self._lock:
            cur = self._conn.execute(
                """SELECT * FROM songs
                   WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?
                   ORDER BY title""",
                (f"%{query}%", f"%{query}%", f"%{query}%"),
            )
            return [dict(r) for r in cur.fetchall()]

    def delete_song(self, song_id):
        with self._lock:
            self._conn.execute(
                "DELETE FROM playlist_songs WHERE song_id = ?", (song_id,)
            )
            self._conn.execute(
                "DELETE FROM songs WHERE id = ?", (song_id,)
            )
            self._conn.commit()

    def update_play_count(self, song_id):
        with self._lock:
            now = datetime.now().isoformat()
            self._conn.execute(
                """UPDATE songs
                   SET play_count = play_count + 1, last_played = ?
                   WHERE id = ?""",
                (now, song_id),
            )
            self._conn.commit()

    # ---- Playlist operations ----

    def create_playlist(self, name):
        now = datetime.now().isoformat()
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO playlists (name, created_at) VALUES (?, ?)",
                (name, now),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_all_playlists(self):
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM playlists ORDER BY name"
            )
            return [dict(r) for r in cur.fetchall()]

    def add_to_playlist(self, playlist_id, song_id):
        with self._lock:
            cur = self._conn.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM playlist_songs "
                "WHERE playlist_id = ?",
                (playlist_id,),
            )
            pos = cur.fetchone()[0]
            try:
                self._conn.execute(
                    "INSERT INTO playlist_songs (playlist_id, song_id, position) "
                    "VALUES (?, ?, ?)",
                    (playlist_id, song_id, pos),
                )
                self._conn.commit()
            except sqlite3.IntegrityError:
                pass

    def get_playlist_songs(self, playlist_id):
        with self._lock:
            cur = self._conn.execute(
                """SELECT s.* FROM songs s
                   JOIN playlist_songs ps ON s.id = ps.song_id
                   WHERE ps.playlist_id = ?
                   ORDER BY ps.position""",
                (playlist_id,),
            )
            return [dict(r) for r in cur.fetchall()]

    # ---- Download operations ----

    def add_download(self, source_url, source_id="", title="", artist=""):
        now = datetime.now().isoformat()
        with self._lock:
            cur = self._conn.execute(
                """INSERT INTO downloads
                   (source_url, source_id, title, artist, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (source_url, source_id, title, artist, now),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_download(self, download_id):
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM downloads WHERE id = ?", (download_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_downloads(self):
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM downloads ORDER BY created_at DESC"
            )
            return [dict(r) for r in cur.fetchall()]

    def update_download(self, download_id, **kwargs):
        with self._lock:
            fields = []
            values = []
            for key, val in kwargs.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(download_id)
            self._conn.execute(
                f"UPDATE downloads SET {', '.join(fields)} WHERE id = ?",
                values,
            )
            self._conn.commit()
