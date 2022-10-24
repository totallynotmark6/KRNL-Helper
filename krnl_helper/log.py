import logging
import os
import queue

from rich.logging import RichHandler
from rich.text import Text

LOGGER_NAME = "krnl_helper"

# define a custom log handler
class CustomLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.messages = queue.deque(maxlen=100)

    def emit(self, record):
        # self.log_callback(self.format(record))
        msg = self.format(record)
        level_name = record.levelname
        time = Text.styled(record.asctime + " ", style="log.time")
        level_text = Text.styled(level_name.ljust(8), f"logging.level.{level_name.lower()}")
        message = Text.styled(record.message, "log.message")
        # msg = msg.format(record.levelname.ljust(8))
        result = time + level_text + message
        self.messages.append(result.markup)

    def get_messages(self):
        return self.messages


ch = None


def init_logger(log_level_for_console: str = "info", log_level_for_file: str = "debug", save_dir: str = None):
    global ch
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level=logging.DEBUG)
    logger.propagate = False

    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s %(lineno)d - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="[%X]")

    # ch = logging.StreamHandler()
    ch = CustomLogHandler()
    ch.setLevel(log_level_for_console.upper())
    ch.setFormatter(console_formatter)
    logger.addHandler(ch)

    if save_dir is not None:
        fh = logging.FileHandler(os.path.join(save_dir, f"{LOGGER_NAME}.txt"))
        fh.setLevel(log_level_for_file.upper())
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)


def get_logger():
    return logging.getLogger(LOGGER_NAME)


def get_console_handler():
    return ch
