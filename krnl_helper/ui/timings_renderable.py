from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from krnl_helper.config import Config
from krnl_helper.schedule import Timings


class TimingsRenderable:
    def __init__(self, config: Config):
        self.timingscls: Timings = None
        self._c_elapsed = "00:00:00"
        self._c_remaining = "00:00:00"

    def render(self, console, options):
        layout = Layout(name="schedule")

        table = Table(show_header=False, show_edge=False, expand=True)
        table.add_column("data", no_wrap=True, overflow="ellipsis")
        if self.timingscls:
            table.add_row(str(self.timingscls.elapsed).split(".")[0])
            table.add_row(str(self.timingscls.remaining).split(".")[0])
        else:
            table.add_row(self._c_elapsed)
            table.add_row(self._c_remaining)
        panel = Panel(table, title="Schedule")

        return panel

    def __rich_console__(self, console, options):
        yield self.render(console, options)
