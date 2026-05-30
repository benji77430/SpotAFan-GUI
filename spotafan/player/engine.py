import random
from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from spotafan.config import Config

class PlayerEngine(QObject):
    song_changed = Signal(dict)
    position_changed = Signal(float)
    duration_changed = Signal(float)
    state_changed = Signal(str)
    volume_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(parent)
        self._audio = QAudioOutput(parent)
        self._player.setAudioOutput(self._audio)
        Config.load_settings()
        self._playlist = []
        self._current_index = -1
        self._shuffle = False
        self._repeat = False
        self._current_song = None

        self._player.positionChanged.connect(
            lambda pos: self.position_changed.emit(pos / 1000.0)
        )
        self._player.durationChanged.connect(
            lambda dur: self.duration_changed.emit(dur / 1000.0)
        )
        self._player.mediaStatusChanged.connect(self._on_media_status)
        self._player.playbackStateChanged.connect(self._on_state_changed)

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next()

    def _on_state_changed(self, state):
        mapping = {
            QMediaPlayer.PlaybackState.PlayingState: "playing",
            QMediaPlayer.PlaybackState.PausedState: "paused",
            QMediaPlayer.PlaybackState.StoppedState: "stopped",
        }
        self.state_changed.emit(mapping.get(state, "stopped"))

    @property
    def volume(self):
        return int(self._audio.volume() * 100)

    @volume.setter
    def volume(self, value):
        self._audio.setVolume(max(0, min(100, value)) / 100.0)
        self.volume_changed.emit(self.volume)

    def set_playlist(self, songs, start_index=0):
        self._playlist = list(songs)
        self._current_index = start_index if self._playlist else -1
        self._load_current()

    def play_song(self, song):
        self._current_song = song
        self._player.setSource(QUrl.fromLocalFile(song["file_path"]))
        self._player.play()
        self.song_changed.emit(song)

    def _load_current(self):
        if 0 <= self._current_index < len(self._playlist):
            song = self._playlist[self._current_index]
            self.play_song(song)

    def play(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            if self._playlist:
                self._load_current()
            elif self._current_song:
                self.play_song(self._current_song)
                Config.set("current_song", self._current_song)
                print("saving musics to settings !")

        else:
            self._player.play()

    def pause(self):
        self._player.pause()

    def stop(self):
        self._player.stop()

    def toggle_play_pause(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()

    def next(self):
        if not self._playlist:
            return
        if self._shuffle:
            candidates = [i for i in range(len(self._playlist))
                          if i != self._current_index]
            if candidates:
                self._current_index = random.choice(candidates)
        else:
            self._current_index += 1
            if self._current_index >= len(self._playlist):
                if self._repeat:
                    self._current_index = 0
                else:
                    self._current_index = -1
                    self._player.stop()
                    return
        self._load_current()

    def previous(self):
        if not self._playlist:
            return
        pos = self._player.position()
        if pos > 3000:
            self._player.setPosition(0)
            return
        if self._shuffle:
            candidates = [i for i in range(len(self._playlist))
                          if i != self._current_index]
            if candidates:
                self._current_index = random.choice(candidates)
        else:
            self._current_index -= 1
            if self._current_index < 0:
                if self._repeat:
                    self._current_index = len(self._playlist) - 1
                else:
                    self._current_index = 0
                    self._player.setPosition(0)
                    return
        self._load_current()

    def seek(self, position_seconds):
        self._player.setPosition(int(position_seconds * 1000))

    def toggle_shuffle(self):
        self._shuffle = not self._shuffle
        return self._shuffle

    def toggle_repeat(self):
        self._repeat = not self._repeat
        return self._repeat

    @property
    def current_song(self):
        return self._current_song

    @property
    def is_playing(self):
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def cleanup(self):
        self._player.stop()
