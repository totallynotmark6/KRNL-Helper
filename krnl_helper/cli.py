from pathlib import Path
from time import sleep

import typer
from rich.live import Live
from rich.tree import Tree

from krnl_helper.config import Config, History
from krnl_helper.log import get_logger, init_logger
from krnl_helper.music import Playlist
from krnl_helper.recording import Record
from krnl_helper.schedule import Schedule, Timings
from krnl_helper.ui import ConsoleUI
from krnl_helper.weather.base import Weather

from .console import console

app = typer.Typer()


@app.command()
def run_server(
    config: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    enable_server: bool = typer.Option(
        None,
        "--enable-server/--disable-server",
        help="Enables or disables the server. The default relies on the config.",
    ),
    # enable_ui: bool = typer.Option(
    #     True,
    #     "--enable-ui/--disable-ui",
    #     help="Enables or disables the UI."
    # )
):
    c = Config.from_file(config)
    init_logger()
    logger = get_logger()
    if c.record_enabled:
        record = Record(c)
    ui = ConsoleUI(c)
    if c.music_enabled:
        history = c.get_history()
        sched = Schedule(c, history)
        sched.generate_schedule()
        sched._prepare_live(0)
        sched._schedule_prepared = True
        ui._schedule_renderable.schedulecls = sched
    if c.timings_enabled:
        t = Timings(c)
        if c.record_enabled:
            t.add_recording(record)
        if c.music_enabled:
            t.add_schedule(sched)
        ui._timings_renderable.timingscls = t
    try:
        with Live(ui, console=console, screen=True):
            while True:
                if c.timings_enabled:
                    t.tick()
                ui.update_data()
                sleep(0.25)
    finally:
        pass

@app.command()
def debug_config(
    config: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    )
):
    c = Config.from_file(config)
    tree = Tree(config.name if config else "<Default>")
    if c.music_enabled:
        mus = tree.add("[green]Music[/green]")
        mus.add(f"App: {c.music_app}")
        mus.add(f"Playlist: {c.music_playlist}")
        mus.add(f"Record to History: {c.music_record_to_history}")
    else:
        tree.add("[black]Music (disabled)[/black]")
    if c.history_enabled:
        hist = tree.add(f"[green]History[/green]")
        hist.add(f"Path: {c.history_path}")
        sched = hist.add("Scheduling")
        sched.add(f"Restricted Sections: {c.history_scheduling_force_unique}")
        sched.add(f"Last Resort Sections: {c.history_scheduling_attempt_unique}")
    else:
        tree.add("[black]History (disabled)[/black]")
    if c.hold_music_enabled:
        hol = tree.add("[green]Hold Music[/green]")
        hol.add(f"App: {c.hold_music_app}")
        hol.add(f"Song: {c.hold_music_song}")
    else:
        tree.add("[black]Hold Music (disabled)[/black]")
    if c.weather_enabled:
        wea = tree.add("[green]Weather[/green]")
        wea.add(f"Service: {c.weather_service}")
        wea.add(f"Location: {c.weather_location}")
    else:
        tree.add("[black]Weather (disabled)[/black]")
    if c.timings_enabled:
        tim = tree.add("[green]Timings[/green]")
        tim.add(f"Duration: {c.timings_duration}")
        tim.add(f"Start: {c.timings_start}")
        tim.add(f"End: {c.timings_end}")
    else:
        tree.add("[black]Timings (disabled)[/black]")
    if c.record_enabled:
        rec = tree.add("[green]Record[/green]")
        rec.add(f"Path: {c.record_path}")
        rec.add(f"Spacing: {c.record_spacing}")
    else:
        tree.add("[black]Record (disabled)[/black]")
    console.print(tree)


@app.command()
def test_command():
    # with console.status("Attempting to run JXA..."):
    #     _run_jxa("Application('Fork').quit()")
    #     _run_jxa("app = Application('Finder'); app.includeStandardAdditions = true; app.displayAlert('hi!')")
    # _run_applescript("tell application \"Spotify\" to play track \"spotify:track:6y0igZArWVi6Iz0rj35c1Y\"")
    # ws = Weather.get_service("OpenMeteo")
    # print(ws.get_current_est().temperature_2m.to("degF"))
    # c = Config.from_file(Path("examples/krnl.json"))
    # r = Record(c)
    p = Playlist.name_of("KRNL Radio")
    p.play()


def cli():
    app()


if __name__ == "__main__":
    app()
