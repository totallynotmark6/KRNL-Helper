import datetime
import subprocess
from datetime import timedelta
from pathlib import Path

from krnl_helper.config import Config


class Record:
    def __init__(self, config: Config):
        self.url = "http://localhost:8080"
        self.path = Path(config.record_path) / config.timings_start.strftime("%Y-%m-%d_%H-%M.mp3")
        self.starts_at = config.timings_start - timedelta(seconds=config.record_spacing)
        self.ends_at = config.timings_end + timedelta(seconds=config.record_spacing)
        self._process = None

    def start(self):
        self._process = subprocess.Popen(
            [
                "ffmpeg",
                "-i",
                self.url,
                "-c",
                "copy",
                str(self.path.resolve()),
            ],
            stdout=subprocess.PIPE,
        )

    def is_running(self):
        return self._process.poll() is None

    def stop(self):
        self._process.terminate()
        self._process.wait()
