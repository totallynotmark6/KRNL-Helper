# Client can technically get everything that the server displays, but by default, it only gets the times, and the schedule.

# This is the client class. It is used to connect to the server and get the data.
import json
import socket
import threading
from multiprocessing.connection import wait
from pathlib import Path
from time import sleep

from krnl_helper.console import console
from krnl_helper.network.utils import network_uncompress
from krnl_helper.statics import NETWORK_MAX_SIZE, NETWORK_TEXT_ENCODING

# message log
# c: client
# s: server
# c->s: "i exist! heres my password"
# s->c: "ok, here's the config, adjust yourself"
# c->s: "done! gimme data :3"
# s->c: "ok, here's the data."
# c->s: "any updates?"
# s->c: "sure, i guess. here ya go!"
# ... and so on


class Client:
    def __init__(self, server_ip, server_port, server_password, wait_for_server=False, wants=[]):
        self._exit = False
        self.server_ip = server_ip
        self.server_port = server_port
        with console.status("Connecting to the server...", spinner="dots12"):
            while True:
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect((self.server_ip, self.server_port))
                    break
                except ConnectionRefusedError:
                    if not wait_for_server:
                        raise
                    sleep(2)
        self.socket.settimeout(0.5)
        self.socket.sendall(server_password.encode(NETWORK_TEXT_ENCODING))
        self.config = json.loads(self.socket.recv(NETWORK_MAX_SIZE).decode(NETWORK_TEXT_ENCODING))
        self.wants = wants or self.config["server"]["client_data"]
        self.socket.sendall(json.dumps(self.wants).encode(NETWORK_TEXT_ENCODING))
        self.thread = threading.Thread(target=self._run)
        self._logs = []
        self._schedule = []
        self._current_time = 0
        self.thread.start()

    def _run(self):
        while not self._exit:
            try:
                decompressed_data = network_uncompress(self.socket.recv(NETWORK_MAX_SIZE))
                match decompressed_data["type"]:
                    case "log":
                        self._logs = decompressed_data["msgs"]
                    case "now_playing_file":
                        with open(Path.home() / "Documents" / "now_playing.txt", "w") as f:
                            f.write(decompressed_data["data"])
                    case "schedule":
                        self._schedule = decompressed_data["data"]
                    case "timings":
                        self._current_time = decompressed_data["elapsed"]
                    case "exit":
                        self._exit = True
                    case _:
                        print(decompressed_data)
            except socket.timeout:
                pass
            except ConnectionResetError:
                break
        self.socket.close()

    def get_logs(self):
        return self._logs

    def get_schedule(self):
        return self._schedule

    def close(self):
        self._exit = True
        self.thread.join()
        self.socket.close()

    @property
    def should_exit(self):
        return self._exit

    def get_current_time(self):
        return self._current_time

    def __del__(self):
        self.close()
