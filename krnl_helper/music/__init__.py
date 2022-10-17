import json
import os
import subprocess
from datetime import datetime, timedelta
from functools import cache
from typing import Union

import rich.repr


@rich.repr.auto
class Song:
    def __init__(self, title: str, artist: str, album: str, duration: Union[timedelta, float], persistentID: str):
        self.title = title
        self.artist = artist
        self.album = album
        if isinstance(duration, timedelta):
            self.duration = duration
        else:
            self.duration = timedelta(seconds=duration)
        self.persistentID = persistentID

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def to_rich_string(self):
        return f"[red]{self.title}[/red] - [blue]{self.artist}[/blue] ([green]{self.duration}[/green])"

    def __eq__(self, other):
        if isinstance(other, Song):
            return self.persistentID == other.persistentID
        return False

    def __hash__(self):
        return hash(self.persistentID)

    def to_json(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration.total_seconds(),
            "persistentID": self.persistentID,
        }

    @classmethod
    def from_applescript_properties(cls, properties):
        return cls(
            properties["name"],
            properties["artist"],
            properties["album"],
            properties["duration"],
            properties["persistentID"],
        )


@rich.repr.auto
class LiveSegment(Song):
    def __init__(self, duration: Union[timedelta, float]):
        super().__init__("Live", "Mark", "what album", duration, "C0FFEE")


class CurrentSong:
    def __init__(self):
        self._song_last_refreshed = datetime.now() - timedelta(minutes=5)
        self._last_song = None
        self._current_position_last_refreshed = datetime.now() - timedelta(minutes=5)
        self._current_position = None

    @property
    def song(self):
        """Gets the current song, re-aligns every 30 seconds OR when the song nears the end."""
        if (
            self._last_song == None
            or self._song_last_refreshed < (datetime.now() - timedelta(seconds=30))
            or self._last_song.duration < (self.current_position + timedelta(seconds=10))
            or self.current_position < timedelta(seconds=2)
        ):
            self._last_song = get_current_song()
            self._song_last_refreshed = datetime.now()
        return self._last_song

    @property
    def current_position(self) -> timedelta:
        """Gets the current position of the song, re-aligns every second."""
        if self._current_position == None or self._current_position_last_refreshed < (
            datetime.now() - timedelta(seconds=1)
        ):
            self._current_position_last_refreshed = datetime.now()
            self._current_position = get_current_position()
        return self._current_position + (datetime.now() - self._current_position_last_refreshed)

    def refresh(self):
        """Forcibly refreshes current_position and the song"""
        self._current_position = None
        self._last_song = None

    def __str__(self):
        try:
            return "Now Playing: " + str(self.song)
        except:
            return "No Song Playing"

    def rich_str(self):
        try:
            song = self.song
            return f"[red]{song.title}[/red] - [blue]{song.artist}[/blue] ([magenta]{self.current_position}[/magenta] / [green]{song.duration}[/green])"
        except:
            return "[red]No Song Playing[/red]"


@rich.repr.auto
class Playlist:
    def __init__(self, name: str, description: str, playlistType: str, persistentID: str):
        self.name = name
        self._description = description
        self.playlistType = playlistType
        self.persistentID = persistentID
        self._songs = None
        self._refreshed = datetime.now() - timedelta(minutes=5)

    @property
    def songs(self):
        """Gets the songs in the playlist, re-aligns every minute."""
        if self._songs == None or self._refreshed < (datetime.now() - timedelta(minutes=1)):
            self._songs = get_all_songs_in_playlist(self.name)
        return self._songs

    def refresh(self):
        """Forces a refresh."""
        self._songs = None

    def play(self):
        """Plays the playlist."""
        play_playlist(self.name)

    @classmethod
    def make_playlist(cls, name: str, description=""):
        """Makes the playlist, if it doesn't exist, and return it"""
        all_names = [x.name for x in get_all_playlists()]
        if name not in all_names:
            make_playlist(name, description)
        return cls.name_of(name)

    @property
    def duration(self):
        res = timedelta(seconds=0)
        for i in [song.duration for song in self.songs]:
            res += i
        return res

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description: str):
        if self.is_read_only:
            raise Exception("Playlist is read only")
        set_playlist_description(self.name, description)
        self._description = description

    @description.deleter
    def description(self):
        if self.is_read_only:
            raise Exception("Playlist is read only")
        set_playlist_description(self.name, "")
        self._description = ""

    @property
    def is_read_only(self):
        return self.playlistType != "userPlaylist"

    def delete_playlist(self):
        """Deletes the current playlist."""
        if self.is_read_only:
            raise Exception("Playlist is read only")
        delete_playlist(self.name)

    def add_songs(self, song: Union[list[Song], Song]):
        if self.is_read_only:
            raise Exception("Playlist is read only")
        if isinstance(song, Song):
            song = [song]
        for s in song:
            add_song_to_playlist(self.name, s)

    def remove_songs(self, song: Union[list[Song], Song]):
        if self.is_read_only:
            raise Exception("Playlist is read only")
        if isinstance(song, Song):
            song = [song]
        for s in song:
            remove_song_from_playlist(self.name, s)

    def clear_songs(self):
        """Clears all songs from the playlist."""
        if self.is_read_only:
            raise Exception("Playlist is read only")
        clear_songs_from_playlist(self.name)

    def __len__(self):
        return len(self.songs)

    @classmethod
    def name_of(cls, name):
        """Returns the playlist with the given name, if it exists."""
        for playlist in get_all_playlists():
            if playlist.name == name:
                return playlist
        return None

    @classmethod
    def from_applescript_properties(cls, properties):
        return cls(
            properties["name"], properties.get("description", ""), properties["class"], properties["persistentID"]
        )


def get_jxa_path(script_name):
    return os.path.join(os.path.dirname(__file__), "jxa", script_name + ".jxa")


def get_all_songs_in_playlist(playlist: str) -> list[Song]:
    """Returns all songs in a playlist. This is uncached!"""
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", get_jxa_path("getAllSongsInPlaylist"), playlist], capture_output=True
    )
    result = json.loads(result.stdout)
    return [Song.from_applescript_properties(song) for song in result]
    # return result[0]


def get_current_song() -> Song:
    """Returns the current song. This is uncached!"""
    try:
        result = subprocess.run(["osascript", "-l", "JavaScript", get_jxa_path("getCurrentSong")], capture_output=True)
        result = json.loads(result.stdout)
        return Song.from_applescript_properties(result)
    except KeyError:
        return None


def get_current_position() -> timedelta:
    """Returns the current position of the song. This is uncached!"""
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", get_jxa_path("getCurrentPosition")], capture_output=True
        )
        return timedelta(seconds=float(result.stdout))
    except ValueError:
        return timedelta(seconds=0)


def play_playlist(playlist: str):
    """Plays a playlist."""
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", get_jxa_path("playPlaylist"), playlist], capture_output=True
    )
    result = json.loads(result.stdout)
    if result["status"] != "success":
        raise Exception("Playlist not found!")


def make_playlist(playlist: str, description=""):
    """Makes a playlist."""
    subprocess.run(
        ["osascript", "-l", "JavaScript", get_jxa_path("makePlaylist"), playlist, description], capture_output=True
    )


def get_all_playlists() -> list[Playlist]:
    """Returns all playlists."""
    result = subprocess.run(["osascript", "-l", "JavaScript", get_jxa_path("getAllPlaylists")], capture_output=True)
    result = json.loads(result.stdout)
    return [Playlist.from_applescript_properties(playlist) for playlist in result]


def set_playlist_description(playlist: str, description: str):
    """Sets the description of a playlist."""
    subprocess.run(
        ["osascript", "-l", "JavaScript", get_jxa_path("setPlaylistDescription"), playlist, description],
        capture_output=True,
    )


def delete_playlist(playlist: str):
    """Deletes a playlist."""
    subprocess.run(["osascript", "-l", "JavaScript", get_jxa_path("deletePlaylist"), playlist], capture_output=True)


def clear_songs_from_playlist(playlist: str):
    """Clears all songs from a playlist."""
    subprocess.run(
        ["osascript", "-l", "JavaScript", get_jxa_path("clearSongsFromPlaylist"), playlist], capture_output=True
    )


def add_song_to_playlist(playlist: str, song: Song):
    """Adds a song to a playlist."""
    subprocess.run(
        ["osascript", "-l", "JavaScript", get_jxa_path("addSongToPlaylist"), playlist, song.persistentID],
        capture_output=True,
    )
