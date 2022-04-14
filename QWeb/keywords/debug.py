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
"""Keywords for controlling debugger."""
import pyautogui
from DebugLibrary import DebugLibrary
from robot.api.deco import keyword
from QWeb.internal.config_defaults import CONFIG

cur_timeout = 0
cur_mode = None


@keyword(tags=("Debug", "Error handling"))
def debug_on(mode: str = 'draw') -> None:
    r"""Start debugger with drawing mode and set default timeout down to 2 sec.

    Examples
    --------
    .. code-block:: robotframework

       debugon    #Start debugger and set timeout to 2sec.
       debugon    debug   #Start debugger with SearchMode debug and set timeout to 2sec.

    Parameters
    ----------
    mode : str
       debug(default) = Highlight(blink) element without executing kw
       draw = Highlight element and execute kw

    Related keywords
    ----------------
    \`DebugOff\`
    """
    dbg = DebugLibrary()
    global cur_mode  # pylint: disable=global-statement
    global cur_timeout  # pylint: disable=global-statement
    cur_mode = CONFIG.get_value('SearchMode')
    cur_timeout = CONFIG.get_value(  # type: ignore[assignment]
        'DefaultTimeout')
    CONFIG.set_value('SearchMode', mode)
    CONFIG.set_value('DefaultTimeout', 2)
    CONFIG.set_value('Debug_Run', True)
    dbg.debug()
    CONFIG.set_value('DefaultTimeout', cur_timeout)


@keyword(tags=("Debug", "Error handling"))
def debug_off() -> None:
    r"""Exit debugger. Set timeout and SearchMode back to default.

    Examples
    --------
    .. code-block:: robotframework

       debugoff

    Related keywords
    ----------------
    \`DebugOn\`
    """
    CONFIG.set_value('SearchMode', cur_mode)
    CONFIG.set_value('DefaultTimeout', cur_timeout)
    CONFIG.set_value('Debug_Run', False)
    pyautogui.hotkey('ctrl', 'D')
