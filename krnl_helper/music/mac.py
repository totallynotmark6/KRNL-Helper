import subprocess

from .base import Music, MusicApp


def _run_applescript(script):
    return subprocess.run(["osascript", "-e", script], capture_output=True)


def _run_jxa(script):
    return subprocess.run(["osascript", "-l", "JavaScript", "-e", script], capture_output=True)


class AppleMusicApp(MusicApp):
    name = "Apple Music"
    system = "Darwin"

    def __init__(self):
        pass


class SpotifyApp(MusicApp):
    name = "Spotify"
    system = "Darwin"

    def __init__(self):
        pass


class MPVApp(MusicApp):
    name = "MPV"
    system = "Darwin"

    def __init__(self):
        pass


Music.register_app(AppleMusicApp)
Music.register_app(SpotifyApp)
Music.register_app(MPVApp)
