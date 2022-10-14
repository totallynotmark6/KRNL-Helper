from datetime import datetime, timedelta

from attr import define
from pint import Quantity, UnitRegistry

from .base import Weather, WeatherService

ureg = UnitRegistry()


@define
class OpenMeteoHour:
    time: datetime
    temperature_2m: Quantity
    apparent_temperature: Quantity
    precipitation: Quantity
    rain: Quantity
    showers: Quantity
    snowfall: Quantity
    snow_depth: Quantity
    weathercode: int
    windspeed_1m: Quantity
    winddirection_10m: Quantity
    windgusts_10m: Quantity


class OpenMeteo(WeatherService):
    name = "OpenMeteo"
    url = "https://api.open-meteo.com/v1/forecast?latitude=41.92&longitude=-91.43&hourly=temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,snow_depth,weathercode,windspeed_10m,winddirection_10m,windgusts_10m&timezone=America%2FChicago"
    _data: dict[str, OpenMeteoHour] = {}

    def _parse(self, data):
        self._data = {}
        for i, time in enumerate(data["hourly"]["time"]):
            self._data[time] = OpenMeteoHour(
                time=datetime.strptime(time, "%Y-%m-%dT%H:00"),
                temperature_2m=ureg.Quantity(data["hourly"]["temperature_2m"][i], ureg.degC),
                apparent_temperature=ureg.Quantity(data["hourly"]["apparent_temperature"][i], ureg.degC),
                precipitation=data["hourly"]["precipitation"][i] * ureg.mm,
                rain=data["hourly"]["rain"][i] * ureg.mm,
                showers=data["hourly"]["showers"][i] * ureg.mm,
                snowfall=data["hourly"]["snowfall"][i] * ureg.cm,
                snow_depth=data["hourly"]["snow_depth"][i] * ureg.m,
                weathercode=data["hourly"]["weathercode"][i],
                windspeed_1m=data["hourly"]["windspeed_10m"][i] * ureg.km / ureg.h,
                winddirection_10m=data["hourly"]["winddirection_10m"][i] * ureg.deg,
                windgusts_10m=data["hourly"]["windgusts_10m"][i] * ureg.km / ureg.h,
            )

    def get_current(self) -> OpenMeteoHour:
        return self._data[datetime.now().strftime("%Y-%m-%dT%H:00")]

    def get_current_est(self) -> OpenMeteoHour:
        now = datetime.now()
        h1 = self._data[now.strftime("%Y-%m-%dT%H:00")]
        h2 = self._data[(now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:00")]
        favor = now.minute / 60
        return OpenMeteoHour(
            time=now,
            temperature_2m=linear_interpolate(h1.temperature_2m, h2.temperature_2m, favor),
            apparent_temperature=linear_interpolate(h1.apparent_temperature, h2.apparent_temperature, favor),
            precipitation=linear_interpolate(h1.precipitation, h2.precipitation, favor),
            rain=linear_interpolate(h1.rain, h2.rain, favor),
            showers=linear_interpolate(h1.showers, h2.showers, favor),
            snowfall=linear_interpolate(h1.snowfall, h2.snowfall, favor),
            snow_depth=linear_interpolate(h1.snow_depth, h2.snow_depth, favor),
            weathercode=h1.weathercode,
            windspeed_1m=linear_interpolate(h1.windspeed_1m, h2.windspeed_1m, favor),
            winddirection_10m=linear_interpolate(h1.winddirection_10m, h2.winddirection_10m, favor),
            windgusts_10m=linear_interpolate(h1.windgusts_10m, h2.windgusts_10m, favor),
        )


def linear_interpolate(a, b, favor):
    if isinstance(a, Quantity):
        units = a.units
        q = type(a)
        a = a.magnitude
        b = b.magnitude
        return q(a + (b - a) * favor, units)
    else:
        return a + (b - a) * favor


Weather.register_service(OpenMeteo)
