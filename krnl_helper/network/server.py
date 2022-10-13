# a class that holds the server side of the network
import base64
import bz2
import json
import socket
import threading
from time import sleep

from krnl_helper.console import console
from krnl_helper.log import get_console_handler, get_logger
from krnl_helper.network import get_local_ip, get_local_ip_mnemonicode
from krnl_helper.statics import NETWORK_COMPRESION_LEVEL, NETWORK_MAX_SIZE


class Server:
    def __init__(self, config) -> None:
        self._exit = False
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
            passw = client.recv(1024)
            if passw:
                break
        if passw != self.password.encode("utf-8"):
            # yeet 'em
            client.close()
            return
        # send config
        client.sendall(self._config.to_json().encode("utf-8"))
        while not self._exit:
            try:
                for data_type in self._config.server_client_data:
                    sleep(0.1)
                    to_send = {"type": data_type}
                    match data_type:
                        case "log":
                            to_send["msgs"] = list(get_console_handler().get_messages())
                        case _:
                            get_logger().warning(f"Unknown data type {data_type}!")
                            pass

                    data = bz2.compress(json.dumps(to_send).encode("utf-8"), NETWORK_COMPRESION_LEVEL)
                    to_send_ready = {"compressed": True}
                    to_send_ready["data"] = base64.b85encode(data).decode("utf-8")
                    sending = json.dumps(to_send_ready).encode("utf-8")
                    client.sendall(sending)
                    if len(sending) >= NETWORK_MAX_SIZE * 0.9:
                        get_logger().warning("Data could be too large! ({} bytes)".format(len(sending)))
            except socket.timeout:
                pass
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break
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
