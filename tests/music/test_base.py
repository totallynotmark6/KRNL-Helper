import platform

import pytest

from krnl_helper.music import Music, MusicApp


def test_get_app():
    if platform.system() != "Darwin":
        pytest.skip("Music is only available on macOS for now!")
    music = Music.get_app("Apple Music")
    assert music is not None
    assert issubclass(music, MusicApp)
    assert music.name == "Apple Music"


def test_register_apps():
    assert len(Music._apps) == 2

    for app in Music._apps:
        assert issubclass(Music._apps[app], MusicApp)
