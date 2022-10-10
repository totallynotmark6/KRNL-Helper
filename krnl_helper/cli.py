from datetime import datetime

import requests

from krnl_helper.weather import get_weather


def get_current_song():
    resp = requests.get("https://public.radio.co/stations/s209f09ff1/status")
    data = resp.json()
    # there's some more useful data here, but this works for now
    return data["current_track"]["title"]


def get_time_until_end():
    now = datetime.now()
    end = datetime(now.year, now.month, now.day, 22, 0, 0)
    return end - now


def cli():
    # w / weather - Get the weather
    # t / time - Get the time
    # s / song - Gets the song and logs it to a file
    # sl / songlist - Prints the song list
    # c / clear - Clears the screen
    # q / quit - Quits the program
    print("Type 'help' for a list of commands.")
    while True:
        cmd = input("> ").lower()
        if cmd in ["w", "weather"]:
            print(get_weather())
        elif cmd in ["t", "time"]:
            print("Time until end: {}".format(get_time_until_end()))
        elif cmd in ["s", "song"]:
            current_song = get_current_song()
            print("Current song: {}".format(current_song))
            with open("songlist.txt", "a+") as f:
                f.seek(0)  # go to the beginning of the file
                if current_song not in f.read():
                    # f.read() leaves the cursor at the end of the file, perfect for appending
                    f.write(current_song + "\n")
        elif cmd in ["sl", "songlist"]:
            print("Song list:")
            with open("songlist.txt", "r") as f:
                print(f.read())
        elif cmd in ["c", "clear"]:
            print("\n" * 100)  # it's probably a hack, but it works.
        elif cmd in ["q", "quit"]:
            exit()
        elif cmd in ["h", "help"]:
            print("w / weather - Get the weather")
            print("t / time - Get the time")
            print("s / song - Gets the song and logs it to a file")
            print("sl / songlist - Prints the song list")
            print("c / clear - Clears the screen")
            print("q / quit - Quits the program")
        else:
            print("Invalid command. Type 'help' for a list of commands.")
