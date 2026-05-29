import os
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from spotafan.config import Config


class LibraryManager(QObject):
    library_changed = Signal()

    def __init__(self, database, parent=None):
        super().__init__(parent)
        self._db = database

    def get_all_songs(self):
        return self._db.get_all_songs()

    def search(self, query):
        return self._db.search_songs(query)

    def get_song(self, song_id):
        return self._db.get_song_by_id(song_id)

    def delete_song(self, song):
        try:
            path = song.get("file_path")
            if path and os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
        self._db.delete_song(song["id"])
        self.library_changed.emit()

    def get_songs_by_artist(self, artist):
        return self._db.search_songs(artist)

    def get_total_duration(self):
        songs = self.get_all_songs()
        return sum(s["duration"] for s in songs if s["duration"])

    def get_song_count(self):
        return len(self.get_all_songs())

    def import_local_file(self, file_path):
        import mutagen
        path = Path(file_path)
        if not path.exists() or path.suffix.lower() not in (
            ".mp3", ".flac", ".ogg", ".wav", ".m4a", ".wma"
        ):
            return None

        audio = mutagen.File(file_path)
        title = str(audio.get("title", [path.stem])[0]) if audio else path.stem
        artist = str(audio.get("artist", ["Unknown Artist"])[0]) if audio else "Unknown Artist"
        album = str(audio.get("album", ["Unknown Album"])[0]) if audio else "Unknown Album"
        duration = audio.info.length if audio and hasattr(audio.info, "length") else 0

        song_id = self._db.add_song(
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            file_path=str(path),
            source_url="",
            source_id="",
        )
        if song_id:
            self.library_changed.emit()
        return self._db.get_song_by_id(song_id) if song_id else None
