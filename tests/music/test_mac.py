import platform

import pytest

from krnl_helper.music import Music, MusicApp

if platform.system() != "Darwin":
    pytest.skip("Cannot test macOS music on non-macOS systems!")
