# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 -            Qentinel Group.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------
from __future__ import annotations
from typing import Optional

import timeit

# pylint: disable=pointless-string-statement
"""
   The purpose of this module is to provide measurement utilities.

   Meas object is either enabled or disabled. When disabled, the calls
   to Meas object are no-ops. The purpose is to be able to leave
   the function calls to the production code and control the
   measurement feature separately.

   The function meas_obj() is
   provided to return the global Meas object.

   Usage:
   from QWeb.internal.meas import meas_obj
   meas_obj().start("outer")
   # some code
   meas_obj().start("inner")
   # some more inner code
   meas_obj().stop()
   meas_obj().stop()
"""


class Meas(object):  # pylint: disable=bad-option-value, useless-object-inheritance

    def __init__(self, enabled: bool = True):
        """When initialized with enabled=False the functions
           are no-ops"""

        if not enabled:
            self.start = lambda a='': None  # type:ignore[assignment]
            self.stop = lambda a=True: None  # type:ignore[assignment]
            self.log = lambda a, b: None  # type:ignore[assignment, misc]

        self.timers: list[tuple[float, str]] = []

    # pylint: disable=method-hidden
    def start(self, comment: str = '') -> None:
        """Start a timer. Can be called multiple times without
           a stop in between."""
        start_t = timeit.default_timer()
        self.timers.append((start_t, comment))

    # pylint: disable=method-hidden
    def stop(self, log: bool = True) -> Optional[float]:
        """Returns the calculated time against last started timer.
           When called multiple times pops always the next available
           timer."""
        stop_t = timeit.default_timer()
        start_t, comment = self.timers.pop()
        t = stop_t - start_t
        if log:
            # pylint: disable=too-many-function-args
            self.log(t, comment)
        return t

    @staticmethod
    def log(t, comment: str, level: str = "info") -> None:
        _level = level.lower().strip()
        _log_setting = "*INFO* "
        if _level and _level in "debug":
            _log_setting = "*DEBUG* "
        elif _level and _level in "trace":
            _log_setting = "*TRACE* "
        print("{}Elapsed time {:.4f} s \t{}".format(_log_setting, t, comment))


# Set to True to enable timing measurements
MEAS: Meas = Meas(True)
