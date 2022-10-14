from datetime import timedelta

from attr import define

from krnl_helper.music.base import BasicSong


@define
class SpotifySong(BasicSong):
    """A representation of a song from Spotify."""

    disc_number: int
    """
    The disc number of the track.
    """

    duration: timedelta
    """
    The length of the track in seconds.
    """

    played_count: int
    """
    The number of times this track has been played.
    """

    track_number: int
    """
    The index of the track in its album.
    """

    starred: bool
    """
    Is the track starred?
    """

    popularity: int
    """
    How popular is this track? 0-100
    """

    id: str
    """
    The ID of the item.
    """

    artwork_url: str
    """
    The URL of the track's album cover.
    """

    album_artist: str
    """
    That album artist of the track.
    """

    spotify_url: str
    """
    The URL of the track.
    """
