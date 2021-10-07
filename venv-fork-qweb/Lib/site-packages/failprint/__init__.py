"""
failprint package.

Run a command, print its output only if it fails.
"""

import os
import sys
from typing import List

WINDOWS = sys.platform.startswith("win") or os.name == "nt"

__all__: List[str] = []  # noqa: WPS410 (the only __variable__ we use)
