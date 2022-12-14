# a class that holds the server side of the network
import json
import socket
import threading
from time import sleep

from krnl_helper.console import console
from krnl_helper.log import get_console_handler, get_logger
from krnl_helper.music import CurrentSong
from krnl_helper.network import (
    get_local_ip,
    get_local_ip_mnemonicode,
    ip_to_mnemonicode,
)
from krnl_helper.network.utils import network_compress
from krnl_helper.schedule import Timings
from krnl_helper.statics import NETWORK_MAX_SIZE, NETWORK_TEXT_ENCODING


class Server:
    def __init__(self, config) -> None:
        self._exit = False
        self.sched = None
        self._config = config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with console.status("Starting server...", spinner="dots12"):
            while True:
                try:
                    self.socket.bind((get_local_ip(), config.server_port))
                    break
                except OSError:
                    sleep(2)
        self.password = config.server_password
        self.socket.listen(3)
        self.socket.settimeout(0.5)
        self.client_threads = []
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        logger = get_logger()
        logger.info("Started server! (addr: {}, port: {})".format(get_local_ip_mnemonicode(), config.server_port))

    def _run(self):
        while not self._exit:
            try:
                client, addr = self.socket.accept()
                client.settimeout(0.5)
                t = threading.Thread(target=self._client_thread, args=(client,))
                t.start()
                self.client_threads.append(t)
            except socket.timeout:
                pass
        self.socket.close()

    def _client_thread(self, client):
        # auth!
        while True:
            passw = client.recv(NETWORK_MAX_SIZE)
            if passw:
                break
        if passw != self.password.encode(NETWORK_TEXT_ENCODING):
            # yeet 'em
            client.close()
            return
        get_logger().info("Client connected! (addr: {})".format(ip_to_mnemonicode(client.getpeername()[0])))
        # send config
        client.sendall(self._config.to_json().encode(NETWORK_TEXT_ENCODING))
        # get wants
        wants = json.loads(client.recv(NETWORK_MAX_SIZE)) or self._config.server.client_data
        while not self._exit:
            try:
                for data_type in wants:
                    sleep(0.1)
                    to_send = {"type": data_type}
                    match data_type:
                        case "log":
                            to_send["msgs"] = list(get_console_handler().get_messages())
                        case "now_playing_file":
                            s = CurrentSong().song
                            tmpl = "{title} - {artist}"
                            try:
                                to_send["data"] = tmpl.format(title=s.title, artist=s.artist)
                            except AttributeError:
                                to_send["data"] = "Silence - The Void"
                        case "schedule":
                            if self.sched:
                                to_send["data"] = self.sched.to_json()
                            else:
                                to_send["data"] = []
                        case "timings":
                            try:
                                if self.timings:
                                    to_send["current_time"] = self.timings.elapsed.total_seconds()
                                    to_send["elapsed"] = str(self.timings.elapsed).split(".")[0]
                                    to_send["remaining"] = str(self.timings.remaining).split(".")[0]
                            except AttributeError:
                                to_send["elapsed"] = "N/A"
                                to_send["remaining"] = "N/A"
                        case _:
                            get_logger().warning(f"Unknown data type {data_type}!")

                    # data = bz2.compress(json.dumps(to_send).encode(NETWORK_TEXT_ENCODING), NETWORK_COMPRESION_LEVEL)
                    # to_send_ready = {"compressed": True}
                    # to_send_ready["data"] = base64.b85encode(data).decode(NETWORK_TEXT_ENCODING)
                    # sending = json.dumps(to_send_ready).encode(NETWORK_TEXT_ENCODING)
                    sending = network_compress(to_send)
                    client.sendall(sending)
                    if len(sending) >= NETWORK_MAX_SIZE * 0.9:
                        get_logger().warning("Data could be too large! ({} bytes)".format(len(sending)))
            except socket.timeout:
                pass
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break
        try:
            client.sendall(network_compress({"type": "exit"}))
        finally:
            client.close()

    def close(self):
        self._exit = True
        try:
            self.thread.join()
            for client in self.client_threads:
                client.join()
        except AttributeError:
            pass

    def __del__(self):
        self.close()
