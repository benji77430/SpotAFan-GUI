import threading,time
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QSlider, QWidget, QSizePolicy,
)


class PlayerBar(QFrame):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
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
        self.title=None
        self.thread_title=threading.Thread(target=self._title_rotate)
        self.thread_title.start()
        self.thread_artist=threading.Thread(target=self._artist_rotate)
        self.thread_artist.start()
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        # Left: song info
        self._song_info = QWidget()
        song_layout = QHBoxLayout(self._song_info)
        self._song_info.setFixedSize(230,72)
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
        self._song_title = QLabel("No track playing")
        self._song_title.setObjectName("title")
        self._song_title.setStyleSheet("font-size: 14px;")
        self._song_artist = QLabel("")
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

        self._shuffle_btn = self._make_ctrl_btn("🔀", "Shuffle")
        self._shuffle_btn.setStyleSheet("font-size: 16px;")

        controls.addWidget(self._shuffle_btn)

        self._prev_btn = self._make_ctrl_btn("⏮", "Previous")
        self._prev_btn.setStyleSheet("font-size: 16px;")
        controls.addWidget(self._prev_btn)

        self._play_btn = self._make_ctrl_btn("▶", "Play", bold=True, big=True)
        self._play_btn.setFixedSize(40, 40)
        self._play_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; color: #000000;
                border-radius: 20px; font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { transform: scale(1.1); }
        """)
        controls.addWidget(self._play_btn)

        self._next_btn = self._make_ctrl_btn("⏭", "Next")
        self._next_btn.setStyleSheet("font-size: 16px;")
        controls.addWidget(self._next_btn)

        self._repeat_btn = self._make_ctrl_btn("🔁", "Repeat")
        self._repeat_btn.setStyleSheet("font-size: 14px;")
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
        container_layout.setContentsMargins(8, 4, 8, 4) # Ajoute un padding interne automatique

        # 3. Tes variables d'origine (strictement inchangées) ajoutées dans le rectangle
        self._vol_btn = self._make_ctrl_btn("🔊", "Volume")
        container_layout.addWidget(self._vol_btn)

        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setFixedWidth(120)
        self._volume_slider.setValue(self._engine.volume)
        container_layout.addWidget(self._volume_slider)

        # 4. On ajoute le rectangle complet dans ton layout de droite d'origine
        right.addWidget(volume_container)

        layout.addLayout(right)

    def _make_ctrl_btn(self, icon, tooltip, bold=False, big=False):
        btn = QPushButton(icon)
        btn.setToolTip(tooltip)
        btn.setObjectName("iconic")
        btn.setFixedSize(32, 32) if not big else None
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        style = "font-size: 18px;" if big else "font-size: 16px;"
        if bold:
            style += " font-weight: bold;"
        style += " background: transparent; border: none; color: #000000;"
        style += " QPushButton:hover { color: #ffffff; }"
        btn.setStyleSheet(style)
        return btn

    def _connect_signals(self):
        self._engine.song_changed.connect(self._on_song_changed)
        self._engine.position_changed.connect(self._on_position_changed)
        self._engine.duration_changed.connect(self._on_duration_changed)
        self._engine.state_changed.connect(self._on_state_changed)

        self._play_btn.clicked.connect(self._engine.toggle_play_pause)
        self._prev_btn.clicked.connect(self._engine.previous)
        self._next_btn.clicked.connect(self._engine.next)
        self._shuffle_btn.clicked.connect(self._toggle_shuffle)
        self._repeat_btn.clicked.connect(self._toggle_repeat)

        self._progress_slider.sliderPressed.connect(
            lambda: setattr(self, '_is_dragging', True)
        )
        self._progress_slider.sliderReleased.connect(self._seek_to_position)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)

    def _on_song_changed(self, song):
        self.title = song.get("title", "Unknown")
        self.artist = song.get("artist", "Unknown Artist")
        
        self._song_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #ffffff;"
        )

        thumb = song.get("thumbnail", "")
        if thumb:
            pixmap = QPixmap()
            if pixmap.loadFromData(
                __import__("requests").get(thumb).content
            ):
                self._cover_label.setPixmap(
                    pixmap.scaled(
                        56, 56,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                return
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

    def _on_state_changed(self, state):
        self._play_btn.setText("⏸" if state == "playing" else "▶")

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
        icon = "🔇" if value == 0 else "🔉" if value < 50 else "🔊"
        self._vol_btn.setText(icon)
<<<<<<< HEAD
    
=======

    def _title_rotate(self):
        CLOSE=False
        while not CLOSE:
            while self.title != None:
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
        CLOSE=False
        while not CLOSE:
            while self.title != None:
                if not len(self.artist) < 30:
                    for i in range(len(self.artist)):
                        self._song_artist.setText(self.artist[i::])
                        time.sleep(0.15)
                        self._song_artist.setText(self.artist)
                else:
                    self._song_artist.setText(self.artist)
                    time.sleep(0.2)

                
            time.sleep(0.05)
>>>>>>> f0867f7f5a784f3e5698c406eb8e80333ddeea22
    @staticmethod
    def _format_time(seconds):
        if seconds < 0:
            return "0:00"
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"
