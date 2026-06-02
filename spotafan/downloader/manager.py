import os
import re
import subprocess
import threading
from pathlib import Path

import yt_dlp
from PySide6.QtCore import QObject, Signal

from spotafan.config import Config


class DownloadManager(QObject):
    progress_updated = Signal(int, float)
    status_changed = Signal(int, str)
    download_finished = Signal(int, dict)
    download_error = Signal(int, str)

    search_completed = Signal(list)
    search_error = Signal(str)

    def __init__(self, database, parent=None):
        super().__init__(parent)
        self._db = database
        self._active_downloads = {}
        self._lock = threading.Lock()

    def search(self, query, max_results=Config.get("max_results",15)):
        def _search():
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "extract_flat": "in_playlist",
                    "ignoreerrors": True,
                    "default_search": "ytsearch{}".format(max_results),
                    "source_address": "0.0.0.0",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch{max_results}:{query}",
                                            download=False)

                results = []
                seen = set()
                if "entries" in info:
                    for entry in info["entries"]:
                        if entry is None:
                            continue
                        vid = entry.get("id") or entry.get("url", "")
                        if vid in seen:
                            continue
                        seen.add(vid)
                        duration = entry.get("duration", 0) or 0
                        results.append({
                            "id": vid,
                            "title": entry.get("title", "Unknown Title"),
                            "artist": entry.get("uploader", "Unknown Artist"),
                            "duration": float(duration),
                            "thumbnail": entry.get("thumbnail", ""),
                            "source_url": f"https://youtube.com/watch?v={vid}",
                            "source_id": vid,
                        })
                print("got search results now downloading thumbnails")
                self.search_completed.emit(results)
            except Exception as e:
                self.search_error.emit(str(e))

        thread = threading.Thread(target=_search, daemon=True)
        thread.start()

    def start_download(self, search_result):
        download_id = self._db.add_download(
            source_url=search_result["source_url"],
            source_id=search_result["source_id"],
            title=search_result["title"],
            artist=search_result["artist"],
        )

        self.status_changed.emit(download_id, "starting")
        self._active_downloads[download_id] = {
            "status": "starting",
            "progress": 0,
        }

        thread = threading.Thread(
            target=self._download_worker,
            args=(download_id, search_result),
            daemon=True,
        )
        thread.start()
        return download_id

    def _sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', "_", name).strip()

    def _download_worker(self, download_id, info):
        out_dir = Config.DOWNLOAD_DIR
        safe_title = self._sanitize_filename(info["title"])
        safe_artist = self._sanitize_filename(info["artist"])
        template = os.path.join(
            str(out_dir),
            f"{safe_artist} - {safe_title}.%(ext)s",
        )

        def progress_hook(d):
            if d["status"] == "downloading":
                pct = 0
                if "total_bytes" in d and d["total_bytes"]:
                    pct = d.get("downloaded_bytes", 0) / d["total_bytes"] * 100
                elif "total_bytes_estimate" in d and d["total_bytes_estimate"]:
                    pct = d.get("downloaded_bytes", 0) / d["total_bytes_estimate"] * 100
                self.progress_updated.emit(download_id, pct)
                self.status_changed.emit(download_id, "downloading")
            elif d["status"] == "finished":
                self.progress_updated.emit(download_id, 100)
                self.status_changed.emit(download_id, "processing")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": template,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": Config.get("audio_format", "mp3"),
                "preferredquality": Config.get("audio_quality", "192"),
            }],
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "embedthumbnail": True,
            "writethumbnail": False,
            "source_address": "0.0.0.0",
            "ffmpeg_location": Config.get("ffmpeg_location", ""),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([info["source_url"]])

            expected_file = os.path.join(
                str(out_dir),
                f"{safe_artist} - {safe_title}.{Config.get('audio_format', 'mp3')}",
            )

            final_path = None
            if os.path.exists(expected_file):
                final_path = expected_file
            else:
                for f in out_dir.iterdir():
                    if safe_title in f.stem and safe_artist in f.stem:
                        final_path = str(f)
                        break

            if not final_path:
                raise FileNotFoundError(
                    f"Downloaded file not found for '{info['title']}'"
                )

            song_id = self._db.add_song(
                title=info["title"],
                artist=info["artist"],
                album="YouTube",
                duration=info["duration"],
                file_path=final_path,
                source_url=info["source_url"],
                source_id=info["source_id"],
                thumbnail=info.get("thumbnail", ""),
            )

            song = self._db.get_song_by_id(song_id) if song_id else None
            if song:
                self._db.update_download(
                    download_id,
                    status="completed",
                    progress=100,
                    file_path=song["file_path"],
                    completed_at=__import__("datetime").datetime.now().isoformat(),
                )
                self.status_changed.emit(download_id, "completed")
                self.download_finished.emit(download_id, song)
            else:
                raise RuntimeError("Failed to register song in library")

        except Exception as e:
            error_msg = str(e)
            self._db.update_download(
                download_id,
                status="error",
                error=error_msg,
            )
            self.status_changed.emit(download_id, "error")
            self.download_error.emit(download_id, error_msg)
        finally:
            self._active_downloads.pop(download_id, None)

    def get_downloads(self):
        return self._db.get_all_downloads()
