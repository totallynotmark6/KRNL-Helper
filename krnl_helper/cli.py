import requests
from datetime import datetime


def get_weather():
    # this currently gets the following:
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
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast?latitude=41.92&longitude=-91.43&hourly=temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,snow_depth,weathercode&daily=weathercode,temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&timezone=America%2FChicago"
    )
    data = resp.json()

    # okay, so we have the data, now we need to parse it.
    # for now, we'll just get the current hour's data
    current_hr_index = data["hourly"]["time"].index(
        datetime.now().strftime("%Y-%m-%dT%H:00")
    )
    return "Current weather: {}°F, feels like {}°F, and I think it's {}.".format(
        data["hourly"]["temperature_2m"][current_hr_index],
        data["hourly"]["apparent_temperature"][current_hr_index],
        weathercode_to_string(data["hourly"]["weathercode"][current_hr_index]),
    )


def get_current_song():
    resp = requests.get('https://public.radio.co/stations/s209f09ff1/status')
    data = resp.json()
    # there's some more useful data here, but this works for now
    return data['current_track']['title']


def weathercode_to_string(code):
    if code == 0:
        return "Clear sky"
    elif code in [1, 2, 3]:
        return "Mainly clear"
    elif code == 2:
        return "Partly cloudy"
    elif code == 3:
        return "Overcast"
    elif code == 45:
        return "Fog"
    elif code == 48:
        return "Depositing rime fog"
    elif code == 51:
        return "Light drizzle"
    elif code == 53:
        return "Moderate drizzle"
    elif code == 55:
        return "Dense drizzle"
    elif code == 56:
        return "Freezing light drizzle"
    elif code == 57:
        return "Freezing dense drizzle"
    elif code == 61:
        return "Slight rain"
    elif code == 63:
        return "Moderate rain"
    elif code == 65:
        return "Heavy rain"
    elif code == 66:
        return "Freezing light rain"
    elif code == 67:
        return "Freezing heavy rain"
    elif code == 71:
        return "Slight snow fall"
    elif code == 73:
        return "Moderate snow fall"
    elif code == 75:
        return "Heavy snow fall"
    elif code == 77:
        return "Snow grains"
    elif code == 80:
        return "Slight rain showers"
    elif code == 81:
        return "Moderate rain showers"
    elif code == 82:
        return "Violent rain showers"
    elif code == 85:
        return "Slight snow showers"
    elif code == 86:
        return "Heavy snow showers"
    elif code == 95:  # central europe only
        return "Slight or moderate thunderstorm"
    elif code == 96:  # central europe only
        return "Thunderstorm with slight hail"
    elif code == 99:  # central europe only
        return "Thunderstorm with heavy hail"


def cli():
    print(get_weather())
    print(get_current_song())
