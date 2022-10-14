import platform
from datetime import timedelta

import rich.repr
from attrs import define


class Music:
    _apps = {}

    @classmethod
    def register_app(cls, app):
        if isinstance(app.system, str):
            if isinstance(app.name, str):
                cls._apps[app.name + "/" + app.system] = app
            elif isinstance(app.name, list):
                for name in app.name:
                    cls._apps[name + "/" + app.system] = app
        elif isinstance(app.system, list):
            if isinstance(app.name, str):
                for system in app.system:
                    cls._apps[app.name + "/" + system] = app
            elif isinstance(app.name, list):
                for name in app.name:
                    for system in app.system:
                        cls._apps[name + "/" + system] = app

    @classmethod
    def get_app(cls, app):
        return cls._apps[app + "/" + platform.system()]


class MusicApp:
    name = "N/A"
    system = "N/A"

    def __init__(self):
        pass

    def is_running(self):
        raise NotImplementedError


@define
class BasicSong:
    """A representation of a song.

    Different music apps provide different information about a song. This class is a basic representation of a song, which other apps can extend.
    """

    title: str
    """The title of the song."""

    artist: str
    """The artist of the song."""

    album: str
    """The album of the song."""

    duration: timedelta
    """The duration of the song."""
