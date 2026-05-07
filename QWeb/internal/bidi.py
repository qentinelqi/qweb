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
from dataclasses import dataclass
from collections import deque
from enum import Enum
# Name change in Selenium 4.44 nightly
try:
    from selenium.webdriver.common.bidi.log import JavaScriptLogEntry
except ImportError:
    from selenium.webdriver.common.bidi.log import JavascriptLogEntry as JavaScriptLogEntry
from QWeb.internal import browser
from typing import Optional, Dict, Any
from QWeb.internal.exceptions import QWebDriverError
import time


# FIXME: Selenium's BiDi API for JS exceptions is inconsistent across browsers.
# Firefox's BiDi logs for JS exceptions do not include 'stackTrace' field,
# while Chrome's do. This causes Selenium's JavaScriptLogEntry.from_json to raise KeyError
# Patch JavaScriptLogEntry.from_json to handle missing 'stackTrace' in Firefox BiDi logs

# Store the original method
original_from_json = JavaScriptLogEntry.from_json.__func__  # type: ignore


def patched_from_json(cls: Any, json: dict[str, Any]) -> Any:
    # If Firefox forgot 'stackTrace', we provide an empty one
    # so the original method doesn't raise a KeyError
    if "stackTrace" not in json:
        json["stackTrace"] = None
    return original_from_json(cls, json)


# Apply the patch
JavaScriptLogEntry.from_json = classmethod(patched_from_json)  # type: ignore


class SourceType(Enum):
    CONSOLE = "console"
    EXCEPTION = "exception"


class LogLevel(Enum):
    ALL = "all"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    LOG = "log"


# support common aliases for log levels
level_aliases = {
    "warning": LogLevel.WARN,
    "err": LogLevel.ERROR,
    "critical": LogLevel.ERROR,
}


@dataclass(frozen=True)
class ConsoleMsg:
    ts: float
    level: LogLevel
    text: str
    url: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    source: SourceType = SourceType.CONSOLE  # 'console' or 'exception'

    def as_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts,
            "level": self.level,
            "text": self.text,
            "location": {
                "url": self.url,
                "line": self.line,
                "column": self.column,
            } if self.url else None,
            "source": self.source.value,
        }


# Maximum number of messages/exceptions to store per session
CONSOLE_MSG_LIMIT = 1000

_console_messages: dict[str, deque[ConsoleMsg]] = {}
_js_exceptions: dict[str, deque[ConsoleMsg]] = {}
_handler_ids = {}
_js_handler_ids = {}


# keyword implemetation functions
def _start_console_capture() -> None:
    """Start capturing console messages.

    Console messages can be only captured when browser is open.
    Messages are automatically cleared when you Close All Browsers
    or when you StopConsoleCapture.

    This keyword requires BiDi (Bidirectional) communication to work.
    BiDi can be enabled in Open Browser keyword by setting bidi to True.

    Captures console messages with the specified level.
    Standard levels: all, debug, info, warn, error, log
    Common aliases: warning (maps to warn), err (maps to error)

    Captures messages until StopConsoleCapture is called.
    GetConsoleMessages or VerifyNoConsoleErrors should be used BEFORE stopping capture,
    as messages are cleared on stop.
    """

    if not _is_bidi_enabled():
        raise QWebDriverError(
            "BiDi (Bidirectional) communication is not enabled. "
            "Please enable BiDi in Open Browser keyword by setting bidi to True."
        )
    driver = browser.get_current_browser()
    session_id = driver.session_id
    if driver is None or session_id is None:
        raise QWebDriverError("Could not get session, no open browser")

    # Limit to CONSOLE_MSG_LIMIT messages per session
    _console_messages[session_id] = deque(maxlen=CONSOLE_MSG_LIMIT)
    _js_exceptions[session_id] = deque(maxlen=CONSOLE_MSG_LIMIT)
    # Use Selenium's BiDi API for console messages
    handler_id = driver.script.add_console_message_handler(
        lambda event: on_console_event(event, session_id)
    )
    _handler_ids[session_id] = handler_id
    # Use Selenium's BiDi API for JS exceptions
    js_handler_id = driver.script.add_javascript_error_handler(
        lambda event: on_js_exception_event(event, session_id)
    )
    _js_handler_ids[session_id] = js_handler_id


def _get_console_messages(
        level: str = "all",
        source: Optional[str] = None,
        contains: Optional[str] = None
) -> list[dict[str, Any]]:

    """Get captured console messages with optional filtering."""
    if not _is_bidi_enabled():
        raise QWebDriverError(
            "BiDi (Bidirectional) communication is not enabled. "
            "Please enable BiDi in Open Browser keyword by setting bidi to True."
        )
    driver = browser.get_current_browser()
    session_id = driver.session_id
    if driver is None or session_id is None:
        raise QWebDriverError("Could not get session, no open browser")

    messages = list(_console_messages.get(session_id, []))
    exceptions = list(_js_exceptions.get(session_id, []))
    all_msgs = messages + exceptions

    # Filter by source if specified
    if source is not None:
        source = source.lower()
        if source in ("console",):
            filtered_msgs = [msg for msg in all_msgs if msg.source == SourceType.CONSOLE]
        elif source in ("js", "exception"):
            filtered_msgs = [msg for msg in all_msgs if msg.source == SourceType.EXCEPTION]
        else:
            raise ValueError(f"Unknown message source: {source}. Use 'console' or 'js'.")
    else:
        filtered_msgs = all_msgs
    if level == LogLevel.ALL.value:
        filtered = filtered_msgs
    else:
        normalized_level = _normalize_msg_level(level)
        filtered = [msg for msg in filtered_msgs if msg.level == normalized_level.value]
    # Filter by contains if specified
    if contains is not None:
        contains_lower = contains.lower()
        filtered = [msg for msg in filtered if contains_lower in msg.text.lower()]
    return [msg.as_dict() for msg in filtered]


def _stop_console_capture() -> None:
    """Stop capturing console messages and clear stored messages.

    Messages are automatically cleared when you Close All Browsers
    """
    if not _is_bidi_enabled():
        raise QWebDriverError("BiDi (Bidirectional) communication is not enabled."
                              "Please enable BiDi in Open Browser keyword by setting bidi to True.")

    driver = browser.get_current_browser()
    session_id = driver.session_id
    if driver is None or session_id is None:
        raise QWebDriverError("Could not get session, no open browser")

    handler_id = _handler_ids.pop(session_id, None)
    if handler_id is not None:
        driver.script.remove_console_message_handler(handler_id)
    js_handler_id = _js_handler_ids.pop(session_id, None)
    if js_handler_id is not None:
        driver.script.remove_javascript_error_handler(js_handler_id)
    # Clear stored messages and exceptions for this session
    _console_messages.pop(session_id, None)
    _js_exceptions.pop(session_id, None)


# Helper functions
def _normalize_msg_level(level: str) -> LogLevel:
    level = level.lower()
    if level in level_aliases:
        return level_aliases[level]
    try:
        return LogLevel(level)
    except ValueError as e:
        raise ValueError(f"Unknown log level: {level}") from e


def _is_bidi_enabled() -> bool:
    driver = browser.get_current_browser()
    caps = driver.capabilities

    bidi_ws = caps.get("webSocketUrl")
    if bidi_ws:
        return True

    return False


def on_console_event(event, session_id) -> None:
    msg = ConsoleMsg(
        ts=time.time(),
        level=getattr(event, "level", LogLevel.ALL),
        text=getattr(event, "message", getattr(event, "text", "")),
        url=getattr(event, "url", None),
        line=getattr(event, "line", getattr(event, "lineNumber", None)),
        column=getattr(event, "column", getattr(event, "columnNumber", None)),
        source=SourceType.CONSOLE
    )
    _console_messages[session_id].append(msg)


def on_js_exception_event(event, session_id) -> None:
    stacktrace = getattr(event, "stacktrace", None)
    if stacktrace and "callFrames" in stacktrace and stacktrace["callFrames"]:
        frame = stacktrace["callFrames"][0]
        url = frame.get("url")
        line = frame.get("lineNumber")
        column = frame.get("columnNumber")
    else:
        url = line = column = None
    msg = ConsoleMsg(
        ts=time.time(),
        level=getattr(event, "level", LogLevel.ERROR),
        text=getattr(event, "text", str(event)),
        url=url,
        line=line,
        column=column,
        source=SourceType.EXCEPTION
    )
    _js_exceptions[session_id].append(msg)
