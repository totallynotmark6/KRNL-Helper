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
