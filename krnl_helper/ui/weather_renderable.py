from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from krnl_helper.config import Config
from krnl_helper.log import get_console_handler
from krnl_helper.weather import weathercode_to_str
from krnl_helper.weather.base import Weather
from krnl_helper.weather.services import OpenMeteoHour


class WeatherRenderable:
    def __init__(self, c):
        self.weather = Weather.get_service(c.weather_service)

    def render(self, console, options):
        layout = Layout()

        table = Table(show_header=False)
        table.add_column("Key")
        table.add_column("Value")

        est: OpenMeteoHour = self.weather.get_current_est()
        temp = round(est.temperature_2m.to("degF").m)
        feels = round(est.apparent_temperature.to("degF").m)
        wind = round(est.windspeed_1m.to("mph").m)
        gusts = round(est.windgusts_10m.to("mph").m)
        rain = round(est.precipitation.to("in").m, 2)
        snow = round(est.snowfall.to("in").m, 2)
        table.add_row("Temperature", f"{temp}°F")
        table.add_row("Feels Like", f"{feels}°F")
        table.add_row("Wind", f"{wind}mph")
        table.add_row("Gusts", f"{gusts}mph")
        table.add_row("Rain", f"{rain}in")
        table.add_row("Snow", f"{snow}in")
        table.add_row("Weathercode", weathercode_to_str(est.weathercode))

        layout.update(table)
        p = Panel(layout, title="Weather")
        return p

    def __rich_console__(self, console, options):
        yield self.render(console, options)
