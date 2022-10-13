from rich.layout import Layout
from rich.table import Table

from krnl_helper.config import Config
from krnl_helper.console import console
from krnl_helper.log import get_console_handler, get_logger
from krnl_helper.ui.log_renderable import LogRenderable


class ConsoleUI:
    def __init__(self, config: Config, is_client: bool = False, client=None):
        self._config = config
        self._is_client = is_client
        self._client = client
        self._log_renderable = LogRenderable()

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
        return l

    def update_data(self):
        if self._is_client:
            pass
        else:
            self._log_renderable.logs = list(get_console_handler().get_messages())

    def __rich_console__(self, console, options):
        yield self.render()
