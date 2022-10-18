from rich.layout import Layout
from rich.table import Table

from krnl_helper.config import Config
from krnl_helper.console import console
from krnl_helper.log import get_console_handler, get_logger
from krnl_helper.ui.log_renderable import LogRenderable
from krnl_helper.ui.schedule_renderable import ScheduleRenderable
from krnl_helper.ui.timings_renderable import TimingsRenderable
from krnl_helper.ui.weather_renderable import WeatherRenderable


class ConsoleUI:
    def __init__(self, config: Config, is_client: bool = False, client=None):
        self._config = config
        self._is_client = is_client
        self._client = client
        self._log_renderable = LogRenderable()
        self._schedule_renderable = ScheduleRenderable()
        if config.weather_enabled:
            self._weather_renderable = WeatherRenderable(config)
        self._timings_renderable = TimingsRenderable(config)

    def render_logs(self):
        layout = Layout()
        table = Table(show_header=False)
        table.add_column("Logs")
        ch = get_console_handler()
        logger = get_logger()
        for log in ch.get_messages():
            table.add_row(log)
        layout.update(table)
        return table

    def render(self):
        l = Layout()
        l.split_column(Layout(name="top"), Layout(name="bottom"))
        l["top"].split_row(Layout(name="schedule"), Layout(name="top_left"))
        l["top_left"].split_column(Layout(name="timings"), Layout(name="weather"))
        l["bottom"].split_row(Layout(name="status"), Layout(name="logs"))
        l["logs"].update(self._log_renderable)
        if self._config.weather_enabled:
            l["weather"].update(self._weather_renderable)
        else:
            l["weather"].visible = False
        if self._config.music_enabled:
            l["schedule"].update(self._schedule_renderable)
            pass
        else:
            l["schedule"].visible = False
        if self._config.timings_enabled:
            l["timings"].update(self._timings_renderable)

        return l

    def update_data(self):
        if self._is_client:
            self._log_renderable.logs = self._client.get_logs()
            self._schedule_renderable.current_time = self._client.get_current_time()
            self._schedule_renderable.schedule = self._client.get_schedule()
        else:
            self._log_renderable.logs = list(get_console_handler().get_messages())
            self._schedule_renderable.current_time = self._timings_renderable.timingscls.elapsed
            self._schedule_renderable.schedule = self._schedule_renderable.schedulecls.to_json()

    def __rich_console__(self, console, options):
        yield self.render()
