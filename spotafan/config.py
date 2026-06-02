import os
import json
from pathlib import Path


class Config:
    

    APP_NAME = "SpotAFan"
    VERSION = "1.0.0"
    APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    THEMES=["dark","light"]
    if os.name != "nt":

        _config_dir = Path.home() / ".config" / "spotafan"
        _data_dir = Path.home() / ".local" / "share" / "spotafan"
    
    else:
        #change the config for windows (use appdata)
        _config_dir = Path.home() / ".config" / "spotafan"
        _data_dir = Path.home() / ".local" / "share" / "spotafan"

    DOWNLOAD_DIR = _data_dir / "music"
    DB_PATH = _data_dir / "library.db"
    CONFIG_FILE = _config_dir / "settings.json"


    DEFAULT_SETTINGS = {
        "download_directory": str(DOWNLOAD_DIR),
        "max_concurrent_downloads": 3,
        "audio_format": "mp3",
        "audio_quality": "192",
        "theme": "light",
        "volume": 80,
        "lang": "en",
        "current_song": "",
        "current_playlist": "",
        "current_time": 0
    }

    

    _settings = dict(DEFAULT_SETTINGS)

    @classmethod
    def ensure_dirs(cls):
        cls._config_dir.mkdir(parents=True, exist_ok=True)
        cls._data_dir.mkdir(parents=True, exist_ok=True)
        cls.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load_settings(cls):
        cls.ensure_dirs()
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE,encoding="utf-8") as f:
                    cls._settings.update(json.load(f))
                
            except (json.JSONDecodeError, OSError):
                pass
    

   
            
    @classmethod
    def save_settings(cls):
        cls.ensure_dirs()
        with open(cls.CONFIG_FILE, "w",encoding="utf-8") as f:
            json.dump(cls._settings, f, indent=2)

    @classmethod
    def get(cls, key, default=None):
        return cls._settings.get(key, default)

    @classmethod
    def set(cls, key, value):
        cls._settings[key] = value
        cls.save_settings()
