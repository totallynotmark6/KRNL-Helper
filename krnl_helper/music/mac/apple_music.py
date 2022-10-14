from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path

from attr import define

from krnl_helper.music.base import BasicSong, MusicApp


@define
class AppleMusicArtwork:
    data: bytes
    description: str


class AppleMusicRatingKind(Enum):
    USER = auto()
    """user-specified rating"""

    COMPUTED = auto()
    """computed rating"""


class AppleMusicCloudStatus(Enum):
    UNKNOWN = auto()
    PURCHASED = auto()
    MATCHED = auto()
    UPLOADED = auto()
    INELIGIBLE = auto()
    REMOVED = auto()
    ERROR = auto()
    DUPLICATE = auto()
    SUBSCRIPTION = auto()
    NO_LONGER_AVAILABLE = auto()
    NOT_UPLOADED = auto()


class AppleMusicMediaKind(Enum):
    SONG = auto()
    MUSIC_VIDEO = auto()
    UNKNOWN = auto()


class AppleMusicPlaylistKind(Enum):
    NONE = auto()
    FOLDER = auto()
    GENIUS = auto()
    LIBRARY = auto()
    MUSIC = auto()
    PURCHASED_MUSIC = auto()


@define
class AppleMusicArtwork:
    """a piece of art within a track or playlist"""

    data: bytes
    """data for this artwork, in the form of a picture"""

    description: str
    """description of artwork as a string"""

    downloaded: bool
    """was this artwork downloaded by Music?"""

    format: str
    """the data format for thie piece of artwork"""

    kind: str
    """kind or purpose of this piece of artwork"""

    raw_data: bytes
    """data for this artwork, in original format"""


@define
class AppleMusicTrack(BasicSong):
    artwork: AppleMusicArtwork

    album_artist: str
    """
    the album artist of the track
    """

    album_disliked: bool
    """
    is the album for this track disliked?
    """

    album_loved: bool
    """
    is the album for this track loved?
    """

    album_rating: int
    """
    the rating of the album for this track (0 to 100)
    """

    album_rating_kind: AppleMusicRatingKind
    """
    the rating kind of the album rating for this track
    """

    bit_rate: int
    """
    the bit rate of the track (in kbps)
    """

    bookmark: timedelta
    """
    the bookmark time of the track in seconds
    """

    bookmarkable: bool
    """
    is the playback position for this track remembered?
    """

    bpm: int
    """
    the tempo of this track in beats per minute
    """

    category: str
    """
    the category of the track
    """

    cloud_status: AppleMusicCloudStatus
    """
    the iCloud status of the track
    """

    comment: str
    """
    freeform notes about the track
    """

    compilation: bool
    """
    is this track from a compilation album?
    """

    composer: str
    """
    the composer of the track
    """

    database_ID: int
    """
    the common, unique ID for this track. If two tracks in different playlists have the same database ID, they are sharing the same data.
    """

    date_added: datetime
    """
    the date the track was added to the playlist
    """

    description: str
    """
    the description of the track
    """

    disc_count: int
    """
    the total number of discs in the source album
    """

    disc_number: int
    """
    the index of the disc containing this track on the source album
    """

    disliked: bool
    """
    is this track disliked?
    """

    downloader_Apple_ID: str
    """
    the Apple ID of the person who downloaded this track
    """

    downloader_name: str
    """
    the name of the person who downloaded this track
    """

    enabled: bool
    """
    is this track checked for playback?
    """

    episode_ID: str
    """
    the episode ID of the track
    """

    episode_number: int
    """
    the episode number of the track
    """

    EQ: str
    """
    the name of the EQ preset of the track
    """

    finish: timedelta
    """
    the stop time of the track in seconds
    """

    gapless: bool
    """
    is this track from a gapless album?
    """

    genre: str
    """
    the music/audio genre (category) of the track
    """

    grouping: str
    """
    the grouping (piece) of the track. Generally used to denote movements within a classical work.
    """

    kind: str
    """
    a text description of the track
    """

    long_description: str
    """
    the long description of the track
    """

    loved: bool
    """
    is this track loved?
    """

    lyrics: str
    """
    the lyrics of the track
    """

    media_kind: AppleMusicMediaKind
    """
    the media kind of the track
    """

    modification_date: datetime
    """
    the modification date of the content of this track
    """

    movement: str
    """
    the movement name of the track
    """

    movement_count: int
    """
    the total number of movements in the work
    """

    movement_number: int
    """
    the index of the movement in the work
    """

    played_count: int
    """
    number of times this track has been played
    """

    played_date: datetime
    """
    the date and time this track was last played
    """

    purchaser_Apple_ID: str
    """
    the Apple ID of the person who purchased this track
    """

    purchaser_name: str
    """
    the name of the person who purchased this track
    """

    rating: int
    """
    the rating of this track (0 to 100)
    """

    rating_kind: AppleMusicRatingKind
    """
    the rating kind of this track
    """

    release_date: datetime
    """
    the release date of this track
    """

    sample_rate: int
    """
    the sample rate of the track (in Hz)
    """

    season_number: int
    """
    the season number of the track
    """

    shufflable: bool
    """
    is this track included when shuffling?
    """

    skipped_count: int
    """
    number of times this track has been skipped
    """

    skipped_date: datetime
    """
    the date and time this track was last skipped
    """

    show: str
    """
    the show name of the track
    """

    sort_album: str
    """
    override string to use for the track when sorting by album
    """

    sort_artist: str
    """
    override string to use for the track when sorting by artist
    """

    sort_album_artist: str
    """
    override string to use for the track when sorting by album artist
    """

    sort_name: str
    """
    override string to use for the track when sorting by name
    """

    sort_composer: str
    """
    override string to use for the track when sorting by composer
    """

    sort_show: str
    """
    override string to use for the track when sorting by show name
    """

    size: int
    """
    the size of the track (in bytes)
    """

    start: timedelta
    """
    the start time of the track in seconds
    """

    time: str
    """
    the length of the track in MM:SS format
    """

    track_count: int
    """
    the total number of tracks on the source album
    """

    track_number: int
    """
    the index of the track on the source album
    """

    unplayed: bool
    """
    is this track unplayed?
    """

    volume_adjustment: int
    """
    relative volume adjustment of the track (-100% to 100%)
    """

    work: str
    """
    the work name of the track
    """

    year: int
    """
    the year the track was recorded/released
    """


@define
class AppleMusicFileTrack(AppleMusicTrack):
    """
    a track representing an audio file (MP3, AIFF, etc.)
    """

    location: Path
    """
    the location of the file represented by this track
    """


@define
class AppleMusicSharedTrack(AppleMusicTrack):
    """
    a track residing in a shared library
    """

    pass


@define
class AppleMusicURLTrack(AppleMusicTrack):
    """
    a track representing a network stream
    """

    address: str
    """
    the URL for this track
    """


@define
class AppleMusicPlaylist(Playlist):
    description: str
    """
    the description of the playlist
    """

    disliked: bool
    """
    is this playlist disliked?
    """

    duration: int
    """
    the total length of all tracks (in seconds)
    """

    name: str
    """
    the name of the playlist
    """

    loved: bool
    """
    is this playlist loved?
    """

    parent: "AppleMusicPlaylist"
    """
    folder which contains this playlist (if any)
    """

    size: int
    """
    the total size of all tracks (in bytes)
    """

    special_kind: AppleMusicPlaylistKind
    """
    special playlist kind
    """

    time: str
    """
    the length of all tracks in MM:SS format
    """

    visible: bool
    """
    is this playlist visible in the Source list?
    """


class AppleMusicApp(MusicApp):
    name = "Apple Music"
    system = "Darwin"

    def __init__(self):
        pass
