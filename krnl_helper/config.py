import json
from datetime import date, datetime, time
from pathlib import Path

from krnl_helper.log import get_logger
from krnl_helper.music import Song


class Config:
    _config = {}
    _history = None

    def __init__(self, overrides: dict = None):
        if overrides is None:
            overrides = {}
        self._config = self.get_default_config()
        for key, value in overrides.items():
            self._config[key].update(overrides.get(key, {}))
        self.validate()

    def validate(self):
        if self.music_enabled:
            pass

        if self.history_enabled:
            pass

        if self.hold_music_enabled:
            pass

        if self.weather_enabled:
            pass

        if self.timings_enabled:
            pass

        if self.record_enabled:
            pass

        if self.server_enabled:
            if self.server_password == "":
                self._config["server"]["password"] = "password"

    @classmethod
    def from_file(cls, path: Path):
        if path:
            with path.open() as f:
                data = json.load(f)
            return cls(data)
        return cls()

    @staticmethod
    def get_default_config():
        return {
            "music": {
                "enabled": False,
                "app": "Apple Music",
                "playlist": "My Playlist",
                "record_to_history": True,
            },
            "history": {
                "enabled": False,
                "path": "history.json",
                "scheduling_force_unique": 1,
                "scheduling_attempt_unique": 5,
            },
            "hold_music": {
                "enabled": False,
                "app": "Apple Music",
                "song": "My Song",
            },
            "weather": {
                "enabled": False,
                "app": "Weather",
                "location": "My Location",
            },
            "timings": {
                "enabled": False,
                "duration": 3600,
                "start": "00:00",
                "end": "01:00",
            },
            "record": {
                "enabled": False,
                "path": "./recordings",
                "spacing": 300,
            },
            "server": {"enabled": False, "port": 8080, "password": "password", "client_data": ["timings", "schedule"]},
        }

    def __repr__(self):
        return repr(self._config)

    def get_history(self):
        if self._history is None:
            if self.history_enabled:
                self._history = History(self.history_path)
            else:
                self._history = History()
        return self._history

    @property
    def music_enabled(self):
        return self._config["music"]["enabled"]

    @property
    def music_app(self):
        return self._config["music"]["app"]

    @property
    def music_playlist(self):
        return self._config["music"]["playlist"]

    @property
    def music_record_to_history(self):
        return self._config["music"]["record_to_history"]

    @property
    def history_enabled(self):
        return self._config["history"]["enabled"]

    @property
    def history_path(self):
        return Path(self._config["history"]["path"].replace("~", str(Path.home())))

    @property
    def history_scheduling_force_unique(self):
        return self._config["history"]["scheduling_force_unique"]

    @property
    def history_scheduling_attempt_unique(self):
        return self._config["history"]["scheduling_attempt_unique"]

    @property
    def hold_music_enabled(self):
        return self._config["hold_music"]["enabled"]

    @property
    def hold_music_app(self):
        return self._config["hold_music"]["app"]

    @property
    def hold_music_song(self):
        return self._config["hold_music"]["song"]

    @property
    def weather_enabled(self):
        return self._config["weather"]["enabled"]

    @property
    def weather_service(self):
        return self._config["weather"]["service"]

    @property
    def weather_location(self):
        return self._config["weather"]["location"]

    @property
    def timings_enabled(self):
        return self._config["timings"]["enabled"]

    @property
    def timings_duration(self):
        return self._config["timings"]["duration"]

    @property
    def timings_start(self):
        # make a datetime object from the string "HH:MM"
        t = time.fromisoformat(self._config["timings"]["start"])
        d = date.today()
        return datetime.combine(d, t)

    @property
    def timings_end(self):
        t = time.fromisoformat(self._config["timings"]["end"])
        d = date.today()
        return datetime.combine(d, t)

    @property
    def record_enabled(self):
        return self._config["record"]["enabled"]

    @property
    def record_path(self):
        return self._config["record"]["path"]

    @property
    def record_spacing(self):
        return self._config["record"]["spacing"]

    def to_json(self, indent=0):
        return json.dumps(self._config, indent=indent)

    @classmethod
    def from_json(cls, data):
        if isinstance(data, dict):
            return cls(data)
        elif isinstance(data, str):
            return cls(json.loads(data))

    def client_override(self, wants):
        get_logger().warning("Client override (NYI): %s", wants)


class History:
    _current_show = []
    _past_shows = []

    def __init__(self, path: Path = None):
        self._path = path
        self._past_shows = self._load_history()

    def _load_history(self):
        if self._path.exists():
            with self._path.open() as f:
                return json.load(f)
        return []

    def _save_history(self):
        if self._path:
            with self._path.open("w") as f:
                json.dump({"current": self._current_show, "past": self._past_shows}, f)

    def add(self, song):
        if isinstance(song, Song):
            self._current_show.append(song.to_json())
        elif isinstance(song, dict):
            self._current_show.append(song)
        self._save_history()

    def get_show(self, show_index):
        if show_index == 0:
            return self._current_show
        else:
            try:
                return self._past_shows[show_index - 1]["songs"]
            except (KeyError, IndexError):
                return {"songs": []}

    def finish_show(self):
        self._past_shows.insert({"end_time": datetime.now(), "songs": self._current_show}, 0)
        self._save_history()
