import base64
import bz2
import json

from krnl_helper.log import get_logger
from krnl_helper.statics import NETWORK_COMPRESION_LEVEL, NETWORK_TEXT_ENCODING


def network_compress(obj):
    dumped_obj = json.dumps(obj).encode(NETWORK_TEXT_ENCODING)
    compressed = bz2.compress(dumped_obj, NETWORK_COMPRESION_LEVEL)
    encoded = base64.b85encode(compressed).decode("utf-8")
    to_send = {
        "compressed": True,
        "data": encoded,
    }
    return json.dumps(to_send).encode(NETWORK_TEXT_ENCODING)


def network_uncompress(data):
    data = json.loads(data.decode(NETWORK_TEXT_ENCODING))
    if data["compressed"]:
        decoded = base64.b85decode(data["data"])
        decompressed = bz2.decompress(decoded)
        return json.loads(decompressed.decode(NETWORK_TEXT_ENCODING))
