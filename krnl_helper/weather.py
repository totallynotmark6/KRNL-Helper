import requests


def get_weather():
    # eventually, i'd like to get the following:
    # - hourly
    #   - temperature
    #   - feels like
    #   - precipitation
    #   - rain
    #   - showers
    #   - snow
    #   - snow depth
    #   - weathercode
    # - daily
    #   - temperature max/min
    #   - weathercode

    # as of right now, i just get current weather. it works well enough for now.
    # fallback / alerts: https://forecast.weather.gov/MapClick.php?lon=-91.41865785322857&lat=41.925749334781926#.Y0OkWi-B3rU
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": "41.92",
            "longitude": "-91.43",
            # "hourly": "temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,snow_depth,weathercode",
            # "daily": "weathercode,temperature_2m_max,temperature_2m_min",
            "current_weather": True,
            "temperature_unit": "fahrenheit",
            "windspeed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "America/Chicago",
        },
    )
    data = resp.json()

    # okay, so we have the data, now we need to parse it.
    # for now, we'll just get the current hour's data
    # current_hr_index = data["hourly"]["time"].index(datetime.now().strftime("%Y-%m-%dT%H:00"))
    return "Current weather: {}°F, and I think it's {}.".format(
        data["current_weather"]["temperature"],
        weathercode_to_str(data["current_weather"]["weathercode"]),
    )


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
