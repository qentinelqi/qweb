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
from robot.api import logger
from selenium.common.exceptions import JavascriptException
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.javascript import create_toast_notification

cur_timeout = 0
cur_mode = None


@keyword(tags=("Debug", "Error handling"))
def debug_on(mode: str = "draw") -> None:
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
    cur_mode = CONFIG.get_value("SearchMode")
    cur_timeout = CONFIG.get_value(  # type: ignore[assignment]
        "DefaultTimeout"
    )
    CONFIG.set_value("SearchMode", mode)
    CONFIG.set_value("DefaultTimeout", 2)
    CONFIG.set_value("Debug_Run", True)
    dbg.debug()
    CONFIG.set_value("DefaultTimeout", cur_timeout)


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
    CONFIG.set_value("SearchMode", cur_mode)
    CONFIG.set_value("DefaultTimeout", cur_timeout)
    CONFIG.set_value("Debug_Run", False)
    pyautogui.hotkey("ctrl", "D")


@keyword(tags=("Debug", "Notify"))
def toast_notify(message: str, type: str = "info", position: str = "center",
                 font_size: int = 18, heading: str = "Test Automation Notification", timeout: int = 3):
   r"""Show toast notification in the browser.

   Displays a temporary notification in the browser window using shadow DOM.
   Useful for visual feedback during debugging and test execution.

   Here are the different types of notifications you can use:

   .. image:: https://github.com/qentinelqi/qweb/raw/master/images/toast_notify.png

   **Warning**
   -----------
   This keyword injects temporary elements into the target application's DOM.
   While the notification is encapsulated in Shadow DOM to minimize side effects,
   there is still a slight potential for interference with the tested application.
   Use primarily for debugging and non-production test runs. The added elements are
   removed automatically after the timeout period.

   Parameters
   ----------
   message : str
      Notification message to display.
   type : str, optional
      Type of notification. Options: "info" (default), "success", "warning", "error".
   position : str, optional
      Position of the toast. Options: "center" (default), "top-left", "top-right", "bottom-left", "bottom-right".
   font_size : int, optional
      Font size of the notification text. Default is 18.
   heading : str, optional
      Heading text of the notification. Default is "Test Automation Notification".
   timeout : int, optional
      Duration in seconds before the notification disappears. Default is 3 seconds.

   Examples
   --------
   .. code-block:: robotframework

      Toast Notify    message=Test step passed!    type=success
      Toast Notify    message=Warning occurred!    type=warning    position=top-right    timeout=5

   Related keywords
   ----------------
   `DebugOn`, `DebugOff`
   """
   try:
      create_toast_notification(message, type, position, font_size, heading, timeout)
      logger.info(f"Toast notification displayed: [{type.upper()}] {message}")
   except JavascriptException as e:
      logger.warn(f"Toast notification failed: {e}")