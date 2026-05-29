from PySide6.QtCore import QObject, Signal


class PlaylistManager(QObject):
    playlist_created = Signal(object)
    playlist_deleted = Signal(int)
    song_added = Signal(int, object)
    song_removed = Signal(int, int)

    def __init__(self, database, parent=None):
        super().__init__(parent)
        self._db = database

    def create_playlist(self, name):
        playlist_id = self._db.create_playlist(name)
        if playlist_id:
            pl = {"id": playlist_id, "name": name}
            self.playlist_created.emit(pl)
            return pl
        return None

    def get_all(self):
        return self._db.get_all_playlists()

    def add_song(self, playlist_id, song):
        self._db.add_to_playlist(playlist_id, song["id"])
        self.song_added.emit(playlist_id, song)

    def remove_song(self, playlist_id, song_id):
        self._db.remove_from_playlist(playlist_id, song_id)
        self.song_removed.emit(playlist_id, song_id)

    def get_songs(self, playlist_id):
        return self._db.get_playlist_songs(playlist_id)
