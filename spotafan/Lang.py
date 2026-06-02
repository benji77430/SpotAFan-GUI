import os
import json
from pathlib import Path
from spotafan.config import Config

class LANG:
    def __init__():
        Config.load_settings()
    DEFAULT_LANGS={"en":"english","fr":"français","es":"Español","de":"Deutsch","it":"Italiano","pt":"Português"}

    _lang={}

    @classmethod
    def load_settings(cls):
        if os.path.exists("spotafan/ui/lang.json"):

            try:
                with open("spotafan/ui/lang.json",encoding="utf-8") as f:
                    cls._lang.update(json.load(f))
                    print(LANG)
                    cls._lang=cls._lang[Config.get("lang","en")]

            except (json.JSONDecodeError, OSError):
                pass
        else:
            print("language file doesn't exist !")
    

   
            
    @classmethod
    def save_settings(cls):
        cls.ensure_dirs()
        with open(cls.LANG_FILE, "w",encoding="utf-8") as f:
            json.dump(cls._settings, f, indent=2)

    @classmethod
    def get(cls, key, default="NO TRANSLATION"):
        return cls._lang.get(key, default)

    @classmethod
    def set(cls, key, value):
        cls._lang[key] = value
        cls.save_settings()
