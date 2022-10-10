from .base import Weather, WeatherService


class OpenMeteo(WeatherService):
    name = "OpenMeteo"

    def __init__(self):
        pass


Weather.register_service(OpenMeteo)
