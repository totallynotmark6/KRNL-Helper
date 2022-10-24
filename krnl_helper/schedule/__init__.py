import itertools
import random
from datetime import date, datetime, time, timedelta

from rich.progress import Progress

from krnl_helper.config import Config, History
from krnl_helper.console import console
from krnl_helper.log import get_logger
from krnl_helper.music import LiveSegment, Playlist, Song
from krnl_helper.recording import Record


class Timings:
    def __init__(self, config: Config):
        self.starts = self._parse_time(config.timings_start)
        self.ends = self._parse_time(config.timings_end)
        self.recording_starts = self.starts - timedelta(seconds=config.record_spacing)
        self.recording_ends = self.ends + timedelta(seconds=config.record_spacing)
        self._record = None
        self._schedule = None
        self._schedule_prepared = True

    def add_schedule(self, schedule):
        if isinstance(schedule, Schedule):
            self._schedule = schedule.to_json()
            self._schedulecls = schedule
        elif isinstance(schedule, list):
            self._schedule = schedule

    def add_recording(self, record):
        if isinstance(record, Record):
            self._record = record
        elif isinstance(record, bool):
            self._record = record

    def is_recording(self):
        return self._record.is_recording

    def is_recording_padding(self):
        now = datetime.now()
        return self.recording_starts <= now <= self.recording_ends

    def current_track(self):
        if self._schedule:
            if self.starts <= datetime.now() <= self.ends:
                currently_elasped = datetime.now() - self.starts
                elapsed = 0
                for i, track in enumerate(self._schedule):
                    elapsed += track["duration"]
                    if currently_elasped.total_seconds() <= elapsed:
                        return i, track
        return None, None

    @property
    def elapsed(self):
        return datetime.now() - self.starts

    @property
    def remaining(self):
        return self.ends - datetime.now()

    def tick(self):
        now = datetime.now()
        if self._record != None:
            if self.recording_starts <= now <= self.recording_ends:
                if isinstance(self._record, Record) and not self._record.is_recording:
                    self._record.start()
            else:
                if isinstance(self._record, Record) and self._record.is_recording:
                    self._record.stop()
        if self._schedule:
            if self.starts <= now <= self.ends:
                if self.current_track()[1]["title"] == "Live" and not self._schedule_prepared:
                    self._schedule_prepared = True
                    if self._schedulecls:
                        self._schedulecls._prepare_live(self.current_track()[0] if self.current_track()[0] else 0)
                        get_logger().info("Prepared schedule!")
                if self.current_track()[1]["title"] != "Live" and self._schedule_prepared:
                    self._schedule_prepared = False
                    if self._schedulecls:
                        get_logger().info("PLAYING SCHEDULED CONTENT!")
                        self._schedulecls._play_live()

    @staticmethod
    def _parse_time(time_str: str):
        if isinstance(time_str, datetime):
            return time_str
        return datetime.combine(date.today(), time.strptime(time_str, "%H:%M"))


class Schedule:
    def __init__(self, config: Config, history: History) -> None:
        # self.p = config
        self.history = history
        self.staging_playlist = Playlist.name_of("KRNL Temporary Playlist")
        if not self.staging_playlist:
            self.staging_playlist = Playlist.make_playlist("KRNL Temporary Playlist")
        self.source_playlist = Playlist.name_of("KRNL Radio")
        self.songs = []
        self._current_song = -1

    def _play_live(self):
        self.staging_playlist.play()

    def _prepare_live(self, index):
        self.staging_playlist.clear_songs()
        if self.songs[index].title == "Live":
            currently_on = index + 1
        else:
            currently_on = index
        while True:
            if self.songs[currently_on].title == "Live":
                break
            else:
                self.staging_playlist.add_songs(self.songs[currently_on])
            currently_on += 1

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

    def to_json(self):
        return [song.to_json() for song in self.songs]

    def generate_schedule(self):
        START_WITH_SONG = True
        LIVE_SEGMENT_FREQUENCY = 20 * 60  # seconds
        LIVE_SEGMENT_LENGTH = 2 * 60  # seconds
        TOTAL_DURATION = 60 * 60  # seconds
        END_PADDING = 60  # seconds
        with Progress(console=console) as progress:
            task = progress.add_task("Generating schedule...", total=TOTAL_DURATION)
            if START_WITH_SONG:
                ns = self._get_next_song()
                self.songs.append(ns)
                progress.advance(task, ns.duration.total_seconds())
                self.songs.append(LiveSegment(LIVE_SEGMENT_LENGTH))
                progress.advance(task, LIVE_SEGMENT_LENGTH)
            else:
                self.songs.append(LiveSegment(LIVE_SEGMENT_LENGTH))
                progress.advance(task, LIVE_SEGMENT_LENGTH)

            st_index = len(self.songs)
            while sum(map(lambda song: song.duration.total_seconds(), self.songs)) < TOTAL_DURATION - END_PADDING:
                while (
                    sum(map(lambda song: song.duration.total_seconds(), self.songs[st_index:])) < LIVE_SEGMENT_FREQUENCY
                ):
                    ns = self._get_next_song()
                    if (
                        sum(map(lambda song: song.duration.total_seconds(), self.songs + [ns]))
                        < TOTAL_DURATION - END_PADDING
                    ):
                        self.songs.append(ns)
                        progress.advance(task, ns.duration.total_seconds())
                    else:
                        break
                if (
                    sum(map(lambda song: song.duration.total_seconds(), self.songs + [ns]))
                    < TOTAL_DURATION - END_PADDING
                ):
                    self.songs.append(LiveSegment(LIVE_SEGMENT_LENGTH))
                    progress.advance(task, LIVE_SEGMENT_LENGTH)
                    st_index = len(self.songs)
                else:
                    self.songs.append(
                        LiveSegment(TOTAL_DURATION - sum(map(lambda song: song.duration.total_seconds(), self.songs)))
                    )
                    progress.advance(
                        task, TOTAL_DURATION - sum(map(lambda song: song.duration.total_seconds(), self.songs))
                    )
            progress.update(task, completed=TOTAL_DURATION)

    def tick(self):
        self.staging_playlist

    def current_time(self):
        pass


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
