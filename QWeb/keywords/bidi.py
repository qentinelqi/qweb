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
"""Keywords that require BiDi (Bidirectional) communication.

"""
from __future__ import annotations
from typing import Optional, Any
from robot.api.deco import keyword
from QWeb.internal.bidi import _start_console_capture, _get_console_messages, _stop_console_capture
from QWeb.internal.exceptions import QWebValueError


@keyword(tags=("DevConsole", "BiDi"))
def start_console_capture() -> None:
    r"""Start capturing console messages.

    Both console messages and JavaScript exceptions are captured for the current browser session.
    Only the last 1000 messages of each type are kept;
    older messages are overwritten as new ones arrive.

    Console messages can be only captured when browser is open.
    Messages are automatically cleared when you Close All Browsers
    or when you StopConsoleCapture.

    This keyword requires BiDi (Bidirectional) communication to work.
    BiDi can be enabled in Open Browser keyword by setting bidi to True.

    Captures messages until StopConsoleCapture is called.
    GetConsoleMessages or VerifyNoConsoleErrors should be used BEFORE stopping capture,
    as messages are cleared on stop.

    Examples
    --------
    .. code-block:: robotframework

        # Start capturing console messages
        StartConsoleCapture

    Related keywords
    ----------------
    `GetConsoleMessages`, `VerifyNoConsoleErrors`, `StopConsoleCapture`
    """
    return _start_console_capture()


@keyword(tags=("DevConsole", "BiDi"))
def get_console_messages(level: str = "all",
                         source: Optional[str] = None,
                         contains: Optional[str] = None
                         ) -> list[dict[str, Any]]:
    r"""List all console messages in browser dev console.

    Returns captured console messages with the specified level.
    Standard levels: all, debug, info, warn, error, log
    Common aliases: warning (maps to warn), err (maps to error)
    Default is "all".

    Arguments
    -----------
    level : str
        Log level to filter messages (default: "all").
    source : str, optional
        Filter by message source. Accepted values:
        - "console": only browser console messages
        - "js" or "exception": only JavaScript exceptions
        If not given, returns both sources.
    contains : str, optional
        Filter messages whose text contains this substring (case-insensitive).

    Examples
    --------
    .. code-block:: robotframework

        ${errors}=    GetConsoleMessages    level=error
        ${warnings}=  GetConsoleMessages    level=warn
        ${all}=       GetConsoleMessages
        ${console}=   GetConsoleMessages    level=error    source=console
        ${js}=        GetConsoleMessages    level=error    source=js
        ${xhr}=       GetConsoleMessages    contains=Network

    Related keywords
    ----------------
    `StartConsoleCapture`, `VerifyNoConsoleErrors`, `StopConsoleCapture`
    """
    return _get_console_messages(level, source, contains)


@keyword(tags=("DevConsole", "BiDi"))
def stop_console_capture() -> None:
    r"""Stop capturing console messages.

    Stops capturing console messages and JavaScript exceptions for the current session.
    All stored messages and exceptions for the session are cleared.
    Use GetConsoleMessages or VerifyNoConsoleErrors BEFORE stopping capture if you need
    to access them.

    Examples
    --------
    .. code-block:: robotframework

        StopConsoleCapture

    Related keywords
    ----------------
    `GetConsoleMessages`, `VerifyNoConsoleErrors`, `StartConsoleCapture`
    """
    return _stop_console_capture()


@keyword(tags=("DevConsole", "BiDi"))
def verify_no_console_errors(source: Optional[str] = None) -> None:
    r"""Verify that there are no console errors or JavaScript exceptions.

    Raises an exception if any error-level messages are found in the browser
    console or JS exceptions.
    By default, checks both sources. Use `source="console"` or `source="js"` to restrict.

    Arguments
    ---------
    source : str, optional
        Filter by message source. Accepted values:
        - "console": only browser console messages
        - "js" or "exception": only JavaScript exceptions
        If not given, checks both sources.

    Examples
    --------
    .. code-block:: robotframework

        VerifyNoConsoleErrors
        VerifyNoConsoleErrors    source=console
        VerifyNoConsoleErrors    source=js

    Related keywords
    ----------------
    `GetConsoleMessages`, `StartConsoleCapture`, `StopConsoleCapture`
    """
    errors = _get_console_messages(level="error", source=source)
    if errors:
        raise QWebValueError(
            "Console errors found: {errors}".format(errors=errors)
        )
