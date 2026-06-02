import threading
import time
import requests
import socket
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap,QIcon, QImage
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QSlider, QWidget, QSizePolicy,
)
from spotafan.player.engine import PlayerEngine
from spotafan.Lang import LANG

BOOTSTRAP_SVGs = {
    "shuffle": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-shuffle" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M0 3.5A.5.5 0 0 1 .5 3H1c2.202 0 3.827 1.24 4.874 2.418.49.552.865 1.102 1.126 1.532.26-.43.636-.98 1.126-1.532C9.173 4.24 10.798 3 13 3v1c-1.798 0-3.173 1.01-4.126 2.082A9.6 9.6 0 0 0 7.556 8a9.6 9.6 0 0 0 1.317 1.918C9.828 10.99 11.204 12 13 12v1c-2.202 0-3.827-1.24-4.874-2.418A10.6 10.6 0 0 1 7 9.05c-.26.43-.636.98-1.126 1.532C4.827 11.76 3.202 13 1 13H.5a.5.5 0 0 1 0-1H1c1.798 0 3.173-1.01 4.126-2.082A9.6 9.6 0 0 0 6.444 8a9.6 9.6 0 0 0-1.317-1.918C4.172 5.01 2.796 4 1 4H.5a.5.5 0 0 1-.5-.5"/><path d="M13 5.466V1.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384l-2.36 1.966a.25.25 0 0 1-.41-.192m0 9v-3.932a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384l-2.36 1.966a.25.25 0 0 1-.41-.192"/></svg>',
    "previous": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-skip-start-fill" viewBox="0 0 16 16"><path d="M4 4a.5.5 0 0 1 1 0v3.248l6.267-3.636c.54-.313 1.232.066 1.232.696v7.384c0 .63-.692 1.01-1.232.697L5 8.753V12a.5.5 0 0 1-1 0z"/></svg>',
    "play": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="black" viewBox="0 0 16 16"><path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/></svg>',
    "pause": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="black" viewBox="0 0 16 16"><path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"/></svg>',
    "next": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" viewBox="0 0 16 16"><path d="M12.5 4a.5.5 0 0 0-1 0v3.248L5.233 3.612C4.713 3.31 4.067 3.789 4.067 4.384v7.232c0 .596.646 1.074 1.167.772L11.5 8.752V12a.5.5 0 0 0 1 0V4z"/></svg>',
    "repeat": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-repeat" viewBox="0 0 16 16"><path d="M11 5.466V4H5a4 4 0 0 0-3.584 5.777.5.5 0 1 1-.896.446A5 5 0 0 1 5 3h6V1.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384l-2.36 1.966a.25.25 0 0 1-.41-.192m3.81.086a.5.5 0 0 1 .67.225A5 5 0 0 1 11 13H5v1.466a.25.25 0 0 1-.41.192l-2.36-1.966a.25.25 0 0 1 0-.384l2.36-1.966a.25.25 0 0 1 .41.192V12h6a4 4 0 0 0 3.585-5.777.5.5 0 0 1 .225-.67Z"/></svg>',
    "volume_up": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" viewBox="0 0 16 16"><path d="M11.536 14.01A8.47 8.47 0 0 0 14 8c0-2.29-.91-4.365-2.384-5.88a1 1 0 1 0-1.48 1.34A6.47 6.47 0 0 1 12 8c0 1.772-.705 3.38-1.848 4.566a1 1 0 1 0 1.384 1.444zm-2.257-2.27A5.47 5.47 0 0 0 10 8c0-1.516-.511-2.913-1.374-4.03a1 1 0 0 0-1.578 1.23A3.48 3.48 0 0 1 8 8c0 .878-.32 1.68-.847 2.304a1 1 0 1 0 1.57 1.234zM6.231 4.093A.5.5 0 0 1 6.5 4.5v7a.5.5 0 0 1-.769.423L3.545 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.045l2.186-1.423a.5.5 0 0 1 .499-.004z"/></svg>',
    "volume_down": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-volume-down-fill" viewBox="0 0 16 16"><path d="M9 4a.5.5 0 0 0-.812-.39L5.825 5.5H3.5A.5.5 0 0 0 3 6v4a.5.5 0 0 0 .5.5h2.325l2.363 1.89A.5.5 0 0 0 9 12zm3.025 4a4.5 4.5 0 0 1-1.318 3.182L10 10.475A3.5 3.5 0 0 0 11.025 8 3.5 3.5 0 0 0 10 5.525l.707-.707A4.5 4.5 0 0 1 12.025 8"/></svg>',
    "volume_mute": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" viewBox="0 0 16 16"><path d="M6.717 3.55A.5.5 0 0 1 7 4v8a.5.5 0 0 1-.812.39L3.825 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06zm7.137 2.096a.5.5 0 0 1 0 .708L11.707 8.5l2.147 2.146a.5.5 0 0 1-.708.708L11 9.207l-2.146 2.147a.5.5 0 0 1-.708-.708L10.293 8.5 8.146 6.354a.5.5 0 1 1 .708-.708L11 7.793l2.146-2.147a.5.5 0 0 1 .707 0z"/></svg>'
}



class PlayerBar(QFrame):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        LANG.load_settings()
        self.running=True
        self._engine = engine
        self._is_dragging = False
        self._duration = 0
        self.setObjectName("player_bar")
        self.setFixedHeight(90)
        self.setStyleSheet("""
            QFrame#player_bar {
                background-color: #181818;
                border-top: 1px solid #282828;
            }
        """)
        self._setup_ui()
        self._connect_signals()
        self.title = None
        self.artist = None
        self.thread_title = threading.Thread(target=self._title_rotate,daemon=True)
        self.thread_title.start()
        self.thread_artist = threading.Thread(target=self._artist_rotate,daemon=True)
        self.thread_artist.start()
        self.old_volume = 50

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        # Left: song info
        self._song_info = QWidget()
        song_layout = QHBoxLayout(self._song_info)
        self._song_info.setFixedSize(230, 72)
        self._song_info.setStyleSheet(
            "border-radius: 4px;"
        )
        song_layout.setContentsMargins(10, 0, 0, 0)
        song_layout.setSpacing(12)

        self._cover_label = QLabel()
        self._cover_label.setFixedSize(56, 56)
        self._cover_label.setStyleSheet(
            "background-color: #282828; border-radius: 4px;"
        )
        self._cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        song_layout.addWidget(self._cover_label)

        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(4)
        self._song_title = QLabel(LANG.get("notrack"))
        self._song_title.setObjectName("title")
        self._song_title.setStyleSheet("font-size: 14px;")
        self._song_artist = QLabel()
        self._song_artist.setObjectName("subtitle")
        info_vbox.addWidget(self._song_title)
        info_vbox.addWidget(self._song_artist)
        song_layout.addLayout(info_vbox)
        song_layout.addStretch()
        layout.addWidget(self._song_info, stretch=1)

        # Center: controls + progress
        center = QWidget()
        center.setStyleSheet(
            "border-radius: 4px;"
        )
        center.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 5, 0, 0)
        center_layout.setSpacing(6)

        # Control buttons
        controls = QHBoxLayout()
        controls.setSpacing(16)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._shuffle_btn = self._make_ctrl_btn("shuffle", LANG.get("shuffle"))
        controls.addWidget(self._shuffle_btn)

        self._prev_btn = self._make_ctrl_btn("previous", LANG.get("previous"))
        controls.addWidget(self._prev_btn)

        # Main Play Button stays big
        self._play_btn = self._make_ctrl_btn("play", LANG.get("play"), bold=True, big=True)
        self._play_btn.setFixedSize(40, 40)
        controls.addWidget(self._play_btn)

        self._next_btn = self._make_ctrl_btn("next", LANG.get("next"))
        controls.addWidget(self._next_btn)

        self._repeat_btn = self._make_ctrl_btn("repeat", LANG.get("repeat"))
        controls.addWidget(self._repeat_btn)
        

        center_layout.addLayout(controls)

        # Progress bar
        progress_row = QHBoxLayout()
        progress_row.setSpacing(8)
        self._time_label = QLabel("0:00")
        self._time_label.setStyleSheet("font-size: 11px; color: #b3b3b3;")
        self._time_label.setFixedWidth(40)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignRight |
                                       Qt.AlignmentFlag.AlignVCenter)

        self._progress_slider = QSlider(Qt.Orientation.Horizontal)
        self._progress_slider.setRange(0, 100)
        self._progress_slider.setValue(0)
        self._progress_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; }
            QSlider::handle:horizontal { width: 12px; height: 12px;
                margin: -4px 0; border-radius: 6px; }
        """)

        self._total_label = QLabel("0:00")
        self._total_label.setStyleSheet("font-size: 11px; color: #b3b3b3;")
        self._total_label.setFixedWidth(40)

        progress_row.addWidget(self._time_label)
        progress_row.addWidget(self._progress_slider, stretch=1)
        progress_row.addWidget(self._total_label)
        center_layout.addLayout(progress_row)

        layout.addWidget(center, stretch=3)

        # Right: volume
        right = QHBoxLayout()
        right.setSpacing(8)
        right.setAlignment(Qt.AlignmentFlag.AlignRight)

        # 1. Création d'un widget conteneur qui accepte le dessin d'arrière-plan
        volume_container = QWidget()
        volume_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        volume_container.setObjectName("VolumeContainer")
        volume_container.setStyleSheet("""
            QWidget#VolumeContainer {
                background-color: #121212;
                border-radius: 6px;
            }
        """)

        # 2. Layout interne du rectangle pour mettre les éléments côte à côte
        container_layout = QHBoxLayout(volume_container)
        container_layout.setSpacing(8)
        container_layout.setContentsMargins(8, 4, 8, 4)

        # 3. Tes variables d'origine (strictement inchangées) ajoutées dans le rectangle
        
        # Volume Button initialization
        self._vol_btn = self._make_ctrl_btn("volume_up", LANG.get("volume"))

        container_layout.addWidget(self._vol_btn)

        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setFixedWidth(120)
        self._volume_slider.setValue(self._engine.volume)
        container_layout.addWidget(self._volume_slider)

        # 4. On ajoute le rectangle complet dans ton layout de droite d'origine
        right.addWidget(volume_container)

        layout.addLayout(right)

    def _make_ctrl_btn(self, svg_key, tooltip, bold=False, big=False):
        btn = QPushButton()
        btn.setToolTip(tooltip)
        btn.setObjectName("iconic")
        btn.setFixedSize(32, 32) if not big else None
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Load SVG vector text dynamically via byte format
        svg_bytes = BOOTSTRAP_SVGs[svg_key].encode('utf-8')
        icon = QIcon()
        icon.addPixmap(QPixmap.fromImage(QImage.fromData(svg_bytes)))
        btn.setIcon(icon)
        
        # Handle Scaling for the central Play/Pause wheel button
        icon_size = 24 if big else 16
        btn.setIconSize(QSize(icon_size, icon_size))
        
        # Style sheet setup to handle clean coloring / rendering
        if big:
            # Play button configuration: white disk backdrop with a dark graphic accent
            style = """
                QPushButton {
                    background-color: #ffffff; border-radius: 20px; border: none;
                    qproperty-icon: url(none); /* forces system icon color inversion lookup */
                    color: black;
                }
                QPushButton:hover { background-color: #f0f0f0; }
            """
        else:
            # Standard transport buttons: borderless flat panels with a muted opacity look
            style = """
                QPushButton { 
                    background: transparent; border: none; opacity: 0.7; 
                }
                QPushButton:hover { opacity: 1.0; }
            """
            
        btn.setStyleSheet(style)
        return btn

    def _connect_signals(self):
        self._engine.song_changed.connect(self._on_song_changed)
        self._engine.position_changed.connect(self._on_position_changed)
        self._engine.duration_changed.connect(self._on_duration_changed)
        self._engine.state_changed.connect(self._on_state_changed)
        self._engine.volume_changed.connect(self._on_engine_volume_changed)
        self._play_btn.clicked.connect(self._engine.toggle_play_pause)
        self._prev_btn.clicked.connect(self._engine.previous)
        self._next_btn.clicked.connect(self._engine.next)
        self._shuffle_btn.clicked.connect(self._toggle_shuffle)
        self._repeat_btn.clicked.connect(self._toggle_repeat)
        self._vol_btn.clicked.connect(self._mute_volume)

        self._progress_slider.sliderPressed.connect(
            lambda: setattr(self, '_is_dragging', True)
        )
        self._progress_slider.sliderReleased.connect(self._seek_to_position)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)

    def _mute_volume(self):
        if self._engine.volume > 0:
            self.old_volume = self._engine.volume
            self._volume_slider.setValue(0)
            PlayerEngine.volume(0)
            self._engine.volume = 0
        elif self._engine.volume == 0:
            self._volume_slider.setValue(self.old_volume)
            PlayerEngine.volume(self.old_volume)
            self._engine.volume = self.old_volume

    def _on_song_changed(self, song):
        print(f"song received : {song}")
        self.title = song.get("title", LANG.get("unknown_track"))
        self.artist = song.get("artist", LANG.get("unknown_artist"))
        
        self._song_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #ffffff;"
        )
        # Récupération de la miniature existante
        thumb = song.get("thumbnail", "")
        
        # Recherche alternative automatique sur Internet si absente
        if not thumb and self.title != LANG.get("unknown_track") and self.title != LANG.get("notrack"):
            thumb = self.fetch_track_cover(self.title, self.artist)

        if thumb:
            try:
                if self.internet:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(
                        requests.get(thumb, timeout=2).content
                    ):
                        self._cover_label.setPixmap(
                            pixmap.scaled(
                                56, 56,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation,
                            )
                        )
                        return
            except Exception:
                pass
                
        self._cover_label.clear()
        self._cover_label.setText("🎵")
        self._cover_label.setStyleSheet(
            "font-size: 24px; background-color: #282828; border-radius: 4px;"
        )

    def _on_position_changed(self, pos_sec):
        if not self._is_dragging:
            self._progress_slider.setValue(int(pos_sec * 1000)
                                           if self._duration > 0 else 0)
            self._time_label.setText(self._format_time(pos_sec))

    def _on_duration_changed(self, dur_sec):
        self._duration = dur_sec
        self._progress_slider.setRange(0, max(1, int(dur_sec * 1000)))
        self._total_label.setText(self._format_time(dur_sec))

    def _get_svg_icon(self, svg_key: str) -> QIcon:
        """Helper to cleanly parse an SVG string from BOOTSTRAP_SVGs into a QIcon."""
        svg_bytes = BOOTSTRAP_SVGs[svg_key].encode('utf-8')
        icon = QIcon()
        icon.addPixmap(QPixmap.fromImage(QImage.fromData(svg_bytes)))
        return icon

    def _on_state_changed(self, state):
        # Completely clear any lingering text strings
        self._play_btn.setText("") 
        
        # Choose the correct key and load the actual vector graphic
        svg_key = "pause" if state == "playing" else "play"
        self._play_btn.setIcon(self._get_svg_icon(svg_key))

    def _toggle_shuffle(self):
        on = self._engine.toggle_shuffle()
        self._shuffle_btn.setStyleSheet(
            "font-size: 16px; background: transparent; border: none; "
            f"color: {'#1db954' if on else '#b3b3b3'};"
        )

    def _toggle_repeat(self):
        on = self._engine.toggle_repeat()
        self._repeat_btn.setStyleSheet(
            "font-size: 16px; background: transparent; border: none; "
            f"color: {'#1db954' if on else '#b3b3b3'};"
        )

    def _seek_to_position(self):
        self._is_dragging = False
        pos_ms = self._progress_slider.value()
        self._engine.seek(pos_ms / 1000.0)

    def _on_volume_changed(self, value):
        self._engine.volume = value
        # Erase the emoji string placeholder
        self._vol_btn.setText("") 
        
        # Toggle the clean Bootstrap graphics dynamically
        if value == 0: svg_key = "volume_mute" 
        if 0 < value <= 50: svg_key = "volume_down"
        if value > 50: svg_key = "volume_up"
        self._vol_btn.setIcon(self._get_svg_icon(svg_key))

    def _on_engine_volume_changed(self, value):
        """Updates the slider position when volume changes via shortcuts."""
        self._volume_slider.blockSignals(True)
        self._volume_slider.setValue(value)
        self._volume_slider.blockSignals(False)
        
        self._vol_btn.setText("")
        if value == 0: svg_key = "volume_mute" 
        if 0 < value <= 50: svg_key = "volume_down"
        if value > 50: svg_key = "volume_up"
        self._vol_btn.setIcon(self._get_svg_icon(svg_key))

    def _title_rotate(self):
        while self.running:
            while self.title is not None:
                self._song_artist.setText(self.artist)
                if not len(self.title) < 20:
                    for i in range(len(self.title)):
                        self._song_title.setText(self.title[i::])
                        time.sleep(0.15)
                    self._song_title.setText(self.title)
                    
                    if not len(self.artist) < 30:
                        for i in range(len(self.artist)):
                            self._song_artist.setText(self.artist[i::])
                            time.sleep(0.15)
                            self._song_artist.setText(self.artist)
                        
                    else:
                        self._song_artist.setText(self.artist)
                        time.sleep(0.2)
                else:
                    self._song_title.setText(self.title)
                    time.sleep(0.2)
                
            time.sleep(0.05)

    def _artist_rotate(self):
        while self.running:
            while self.title is not None:
                if not len(self.artist) < 30:
                    for i in range(len(self.artist)):
                        self._song_artist.setText(self.artist[i::])
                        time.sleep(0.15)
                        self._song_artist.setText(self.artist)
                else:
                    self._song_artist.setText(self.artist)
                    time.sleep(0.2)
                
            time.sleep(0.05)

    @staticmethod
    def _format_time(seconds):
        if seconds < 0:
            return "0:00"
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"

    @staticmethod
    def fetch_track_cover(title, artist=""):
        """Recherche automatique via l'API publique et gratuite d'iTunes."""
        def check_internet(ip="8.8.8.8",port=53,timeout=2):
            try:
                socket.setdefaulttimeout(timeout)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip,port))
                return True
            except socket.error as ex:
                print(ex)
                return False
        if check_internet():
            query = f"{title} {artist}".strip()
            url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&entity=song&limit=1"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("resultCount", 0) > 0:
                        cover_url = data["results"][0]["artworkUrl100"]
                        return cover_url.replace("100x100bb", "600x600bb")
            except Exception as e:
                print(f"Erreur de jaquette: {e}")
            return ""
        return ""