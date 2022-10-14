from . import services as _
from .base import *


def weathercode_to_str(code):
    res = ""
    match code:
        case 0:
            res = "Clear sky"
        case 1 | 2 | 3:
            res = "Mainly clear"
        case 2:
            res = "Partly cloudy"
        case 3:
            res = "Overcast"
        case 45:
            res = "Fog"
        case 48:
            res = "Depositing rime fog"
        case 51:
            res = "Light drizzle"
        case 53:
            res = "Moderate drizzle"
        case 55:
            res = "Dense drizzle"
        case 56:
            res = "Freezing light drizzle"
        case 57:
            res = "Freezing dense drizzle"
        case 61:
            res = "Slight rain"
        case 63:
            res = "Moderate rain"
        case 65:
            res = "Heavy rain"
        case 66:
            res = "Freezing light rain"
        case 67:
            res = "Freezing heavy rain"
        case 71:
            res = "Slight snow fall"
        case 73:
            res = "Moderate snow fall"
        case 75:
            res = "Heavy snow fall"
        case 77:
            res = "Snow grains"
        case 80:
            res = "Slight rain showers"
        case 81:
            res = "Moderate rain showers"
        case 82:
            res = "Violent rain showers"
        case 85:
            res = "Slight snow showers"
        case 86:
            res = "Heavy snow showers"
        case 95:  # central europe only
            res = "Slight or moderate thunderstorm"
        case 96:  # central europe only
            res = "Thunderstorm with slight hail"
        case 99:  # central europe only
            res = "Thunderstorm with heavy hail"
        case _:
            res = "Unknown weather"
    return res


__all__ = ["Weather", "WeatherService", "weathercode_to_str"]
