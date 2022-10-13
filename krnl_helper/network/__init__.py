import socket

import mnemonicode


def get_local_ip():
    """Returns the local IP address of the machine."""
    return socket.gethostbyname(socket.gethostname())


def get_local_ip_mnemonicode():
    """Returns the local IP address of the machine in mnemonicode."""
    ip = get_local_ip()
    if ip.count(".") == 3:
        return "-".join(mnemonicode.index_to_word(int(i)) for i in ip.split("."))
    return mnemonicode.mnformat(get_local_ip().encode("utf-8"))


def ip_from_mnemonicode(mn):
    """Returns the IP address from mnemonicode."""
    if mn.count("-") == 3:
        return ".".join(str(mnemonicode.word_to_index(i)) for i in mn.split("-"))
    else:
        return mnemonicode.mnparse(mn).decode("utf-8")
