from .base import Music, MusicApp


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


Music.register_app(AppleMusicApp)
Music.register_app(SpotifyApp)
