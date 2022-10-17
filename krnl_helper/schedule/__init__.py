import itertools
import random

from krnl_helper.config import Config, History
from krnl_helper.log import get_logger
from krnl_helper.music import LiveSegment, Playlist, Song


class Schedule:
    def __init__(self, config: Config, history: History) -> None:
        # self.p = config
        self.history = history
        self.staging_playlist = Playlist.name_of("KRNL Temporary Playlist")
        if not self.staging_playlist:
            self.staging_playlist = Playlist.make_playlist("KRNL Temporary Playlist")
        self.source_playlist = Playlist.name_of("KRNL Radio")
        self.songs = []

    def _get_next_song(self):
        valid_songs = self.source_playlist.songs
        forcibly_excluded_songs = self.history.get_show(0)
        hopefully_excluded_songs = list(
            itertools.chain.from_iterable(map(lambda show: self.history.get_show(show)["songs"], range(1, 6)))
        )
        actually_valid_songs = [
            song for song in valid_songs if song.to_json() not in forcibly_excluded_songs + hopefully_excluded_songs
        ]
        if not actually_valid_songs:
            actually_valid_songs = [song for song in valid_songs if song.to_json() not in forcibly_excluded_songs]
        if not actually_valid_songs:
            # really? no songs?
            # there's no good way to handle this, so just pick a random song
            get_logger().warning("No songs available! Picking a random song...")
            ch = random.choice(valid_songs)
        else:
            ch = random.choice(actually_valid_songs)
        self.history.add(ch)
        return ch

    def generate_schedule(self):
        START_WITH_SONG = True
        LIVE_SEGMENT_FREQUENCY = 20 * 60  # seconds
        LIVE_SEGMENT_LENGTH = 2 * 60  # seconds
        TOTAL_DURATION = 60 * 60  # seconds
        END_PADDING = 60  # seconds

        if START_WITH_SONG:
            self.songs.append(self._get_next_song())
            self.songs.append(LiveSegment(LIVE_SEGMENT_LENGTH))
        else:
            self.songs.append(LiveSegment(LIVE_SEGMENT_LENGTH))
        st_index = len(self.songs)
        while sum(map(lambda song: song.duration.total_seconds(), self.songs)) < TOTAL_DURATION - END_PADDING:
            while sum(map(lambda song: song.duration.total_seconds(), self.songs[st_index:])) < LIVE_SEGMENT_FREQUENCY:
                ns = self._get_next_song()
                if (
                    sum(map(lambda song: song.duration.total_seconds(), self.songs + [ns]))
                    < TOTAL_DURATION - END_PADDING
                ):
                    self.songs.append(ns)
                else:
                    break
            if sum(map(lambda song: song.duration.total_seconds(), self.songs + [ns])) < TOTAL_DURATION - END_PADDING:
                self.songs.append(LiveSegment(LIVE_SEGMENT_LENGTH))
                st_index = len(self.songs)
            else:
                self.songs.append(
                    LiveSegment(TOTAL_DURATION - sum(map(lambda song: song.duration.total_seconds(), self.songs)))
                )


## 1 ##


def index_of_max(l):
    max_value = l[0]
    max_index = 0
    for i, value in enumerate(l):
        if value > max_value:
            max_value = value
            max_index = i
    return max_index


## 2 ##


def sum_of_digits(n):
    if n < 10:
        return n
    return n % 10 + sum_of_digits(n // 10)
