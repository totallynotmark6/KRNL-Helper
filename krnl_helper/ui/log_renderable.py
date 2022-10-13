from rich.layout import Layout
from rich.table import Table

from krnl_helper.log import get_console_handler


class LogRenderable:
    def __init__(self):
        self.logs = []

    def render(self, console, options):
        layout = Layout()

        table = Table(show_header=False)
        table.add_column("Message")

        rows = self.logs

        # This would also get the height:
        render_map = layout.render(console, options)
        n_rows = render_map[layout].region.height

        while n_rows >= 0:
            table = Table(show_header=False)
            table.add_column("Message")

            for row in rows[-n_rows:]:
                table.add_row(row)

            layout.update(table)

            render_map = layout.render(console, options)

            if len(render_map[layout].render[-1]) > 2:
                # The table is overflowing
                n_rows -= 1
            else:
                break

        return table

    def __rich_console__(self, console, options):
        yield self.render(console, options)
