from pathlib import Path
from time import sleep

import typer
from rich.live import Live
from rich.tree import Tree

from krnl_helper.config import Config
from krnl_helper.log import get_console_handler, get_logger, init_logger
from krnl_helper.music.mac import _run_applescript, _run_jxa
from krnl_helper.network import (
    get_local_ip,
    get_local_ip_mnemonicode,
    ip_from_mnemonicode,
)
from krnl_helper.network.client import Client
from krnl_helper.network.server import Server
from krnl_helper.ui import ConsoleUI

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
    )
):
    c = Config.from_file(config)
    init_logger()
    logger = get_logger()
    if c.server_enabled:
        server = Server(c)
    ui = ConsoleUI(c)
    try:
        with Live(ui, console=console, screen=True):
            while True:
                # console.print(ui.render())
                ui.update_data()
                sleep(0.25)
    except KeyboardInterrupt:
        server.close()


@app.command()
def run_client(
    server: str = typer.Option(
        None,
        "--server",
        "-s",
        help="Server address",
        prompt="Server address",
    ),
    server_port: int = typer.Option(
        8080,
        "--server-port",
        "-p",
        help="Server port",
    ),
    server_password: str = typer.Option(
        None,
        "--password",
        help="Server password",
        prompt="Server password",
        hide_input=True,
    ),
    wait_for_server: bool = typer.Option(
        False,
        "--wait-for-server",
        help="Wait for server to start",
    ),
    wants: list[str] = typer.Option(
        [],
        "--wants",
        "-w",
        help="What data to get from server",
    ),
):
    client = Client(ip_from_mnemonicode(server), server_port, server_password, wait_for_server, wants)
    config = Config().from_json(client.config)
    config.client_override(wants)
    ui = ConsoleUI(config, True, client)
    try:
        with Live(ui, console=console, screen=True):
            while True:
                ui.update_data()
                sleep(0.25)
            # sleep(55)
    except KeyboardInterrupt:
        client.close()


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
    if c.server_enabled:
        ser = tree.add("[green]Server[/green]")
        ser.add(f"Code: {get_local_ip_mnemonicode()} ({get_local_ip()})")
        ser.add(f"Port: {c.server_port}")
        ser.add(f"Password: {c.server_password}")
        ser.add(f"Client Data: {c.server_client_data}")
    else:
        tree.add("[black]Server (disabled)[/black]")
    console.print(tree)


@app.command()
def test_command():
    with console.status("Attempting to run JXA..."):
        _run_jxa("Application('Fork').quit()")
        _run_jxa("app = Application('Finder'); app.includeStandardAdditions = true; app.displayAlert('hi!')")
    # _run_applescript("tell application \"Spotify\" to play track \"spotify:track:6y0igZArWVi6Iz0rj35c1Y\"")


def cli():
    app()


if __name__ == "__main__":
    app()
