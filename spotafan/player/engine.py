import random,time
from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from spotafan.config import Config
from spotafan.Lang import LANG

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
        LANG.load_settings()
        self._audio.setVolume(max(0, min(100, Config.get("volume"))) / 100.0)
        self._playlist = []
        self._current_index = -1
        self._shuffle = False
        self._repeat = False
        self._current_song = None
        self._startup_time_restored = False
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
            if self._player.position() > 1000:
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

    def set_volume(self, value):
        """Helper function for shortcut triggers."""
        self.volume = value

    @volume.setter
    def volume(self, value):
        self._audio.setVolume(max(0, min(100, value)) / 100.0)
        self.volume_changed.emit(self.volume)

    def set_playlist(self, songs, start_index=0,restart=False):
        self._playlist = list(songs)
        self._current_index = start_index if self._playlist else -1
        Config.set("current_playlist", self._playlist)
        self._load_current(restart)

    def play_song(self, song,restart=False):
        if not song==None:
            
            self._current_song = song
            Config.set("current_song",song)
            self._player.setSource(QUrl.fromLocalFile(song["file_path"]))
            self._player.play()
            saved_time = Config.get("current_time", None)
            if saved_time is not None and restart and int(saved_time) > 0:
                
                def restore_position(status):
                        # LoadedMedia or BufferedMedia indicates FFmpeg successfully parsed the file headers
                        if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
                            self._player.setPosition(int(saved_time))
                            print(f"Successfully restored time to: {saved_time / 1000.0}s")
                            
                            # Disconnect the temporary hook so it doesn't run on standard track changes
                            try:
                                self._player.mediaStatusChanged.disconnect(restore_position)
                            except RuntimeError:
                                pass # Catch edge case if already disconnected

                # Connect to the status changed signal
                self._player.mediaStatusChanged.connect(restore_position)
                self.pause()
                self._startup_time_restored = True
            self.song_changed.emit(song)

    

    def _load_current(self,restart=False):
        if 0 <= self._current_index < len(self._playlist):
            song = self._playlist[self._current_index]
            self.play_song(song,restart)

    def play(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            if self._playlist:
                self._load_current()
            elif self._current_song:
                self.play_song(self._current_song)

        else:
            self._player.play()

    def step_position(self, seconds):
        """Adjusts the current playback position forward or backward by a delta of seconds."""
        # QMediaPlayer tracks position in milliseconds
        current_pos_ms = self._player.position()
        duration_ms = self._player.duration()
        
        # Calculate new position target
        target_pos_ms = current_pos_ms + (seconds * 1000)
        
        # Keep the target bounded between 0 and the actual track duration
        final_pos_ms = max(0, min(duration_ms, target_pos_ms))
        
        self._player.setPosition(final_pos_ms)
        print(f"moved to {target_pos_ms}")
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
        print(f"current time : {int(self._player.position()) / 1000.0}")
        Config.set("current_time",int(self._player.position()))
        self._player.stop()
