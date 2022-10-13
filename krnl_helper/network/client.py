# Client can technically get everything that the server displays, but by default, it only gets the times, and the schedule.

# This is the client class. It is used to connect to the server and get the data.
import base64
import bz2
import json
import socket
import threading
from multiprocessing.connection import wait
from time import sleep

from krnl_helper.console import console
from krnl_helper.statics import NETWORK_MAX_SIZE

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
    def __init__(self, server_ip, server_port, server_password, wait_for_server=False):
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
        self.socket.sendall(server_password.encode("utf-8"))
        self.config = json.loads(self.socket.recv(1024))
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        while not self._exit:
            try:
                data = json.loads(self.socket.recv(NETWORK_MAX_SIZE))
                match data["type"]:
                    case "log":
                        compressed = base64.b85decode(data["data"])
                        messages = json.loads(bz2.decompress(compressed))
                        print(messages[0])
                    case _:
                        print(data)
            except socket.timeout:
                pass
            except ConnectionResetError:
                break
        self.socket.close()

    def close(self):
        self._exit = True
        self.thread.join()
        self.socket.close()

    def __del__(self):
        self.close()
