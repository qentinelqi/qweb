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
"""Robot framework secrets handling.

In Robot FW logs following things may expose secrets:
    - "start keyword" log item
    - "end keyword" log item
    - Logs printed out inside the keyword implementation

For "start keyword" and "end keyword" filtering is applied:
instead of plain parameter only "*****" is printed.

For other logging, logs will be disabled. This ensures there's
no secrets in XML or HTML files.

Following adds secrets filtering to a keyword function "type_secret":
    from QWeb.internal import secrets
    secrets.add_filter("Type Secret", 1)

 Note the function name vs. name used in the add_filter.
"""

from __future__ import annotations
from typing import Any, Optional, Callable
from robot.version import get_version as rfw_version
from robot.model.keyword import Keyword
from robot.output.logger import LOGGER

try:  # exists only in rf7+
    from robot.output.logger import start_body_item, end_body_item
except ImportError:
    # dummy decorators for rfs below 7
    def start_body_item(fn):
        return fn

    def end_body_item(fn):
        return fn


from robot.libraries.BuiltIn import BuiltIn


def _replace_keyword_args(keyword: Keyword, args: tuple) -> None:
    """Replace keyword args with the provided args

    This function was added to support also RFW 4.0/5.0 RFW changes.
    """
    try:
        keyword.args = args
        return

    except AttributeError:
        # Robot Framework 4.0/5.0 has ModelCombiner object that fails with this
        pass

    # Update according to the ModelCombiner object interface
    if hasattr(keyword.result, "args"):
        setattr(keyword.result, "args", args)
    if hasattr(keyword.data, "args"):
        setattr(keyword.data, "args", args)


def _hide_keyword_arg_values(keyword: Keyword) -> list[str]:
    if hasattr(keyword, "kwname"):
        par_index, secret = FILTERED_KEYWORDS[keyword.kwname]
    else:  # rfw 7
        # name is in different format
        kw_name = "".join(
            f" {char}" if char.isupper() else char.strip() for char in keyword.name
        ).strip()
        par_index, secret = FILTERED_KEYWORDS[kw_name]
    censored_args = list(keyword.args)
    if secret == "hint":
        censored_args[par_index] = "SECRET"
    else:
        censored_args[par_index] = "*" * 5

    return censored_args


def _filtered_start_keyword(keyword: Keyword) -> None:
    """Modify Robot FW internal function "start_keyword".

    This function removes secret data from "start keyword"
    logs and disables logging during the keyword.
    """
    # pylint: disable=protected-access, global-statement
    global LOG_LEVEL
    apply_filter = keyword.kwname in FILTERED_KEYWORDS
    original_args = keyword.args
    if apply_filter:
        censored_args = _hide_keyword_arg_values(keyword)
        _replace_keyword_args(keyword, tuple(censored_args))

    if hasattr(LOGGER, "_log_message"):
        LOGGER.log_message = LOGGER._log_message
    for start_logger in LOGGER.start_loggers:
        start_logger.start_keyword(keyword)

    if apply_filter:
        _replace_keyword_args(keyword, tuple(original_args))
        b = BuiltIn()
        # Disable logging and store previous log level
        if "INFO" not in b.get_variables()["${LOG_LEVEL}"]:
            LOG_LEVEL = b.set_log_level("INFO")
        if DEBUGFILE_LOG_MSG_FN:
            LOGGER._other_loggers[0].log_message = lambda x: None


@start_body_item
def _filtered_start_library_keyword(self, data: Keyword, implementation: Keyword, result: Keyword):
    """Modify Robot FW 7+ internal function "start_library_keyword".

    This function removes secret data from "start library keyword"
    logs and disables logging during the keyword.
    """
    # pylint: disable=protected-access
    # using implementation.name as data.name is in slightly different format
    apply_filter = implementation.name in FILTERED_KEYWORDS
    original_args = data.args

    if apply_filter:
        censored_args = _hide_keyword_arg_values(data)
        _hide_keyword_arg_values(result)
        _replace_keyword_args(data, tuple(censored_args))
        _replace_keyword_args(result, tuple(censored_args))

    for start_logger in self.start_loggers:
        start_logger.start_library_keyword(data, implementation, result)

    if apply_filter:
        _replace_keyword_args(data, tuple(original_args))
        _replace_keyword_args(result, tuple(original_args))
        OTHER_LOGGERS.clear()
        for other in self._other_loggers:
            OTHER_LOGGERS.append((other, other.log_message))
            other.log_message = lambda x: None


def _filtered_end_keyword(keyword: Keyword) -> None:
    """Modify Robot FW internal function "end_keyword".

    This function removes secret data from "end keyword"
    logs and returns previous log level.
    """
    # pylint: disable=protected-access
    apply_filter = keyword.kwname in FILTERED_KEYWORDS
    original_args = keyword.args
    if apply_filter:
        censored_args = _hide_keyword_arg_values(keyword)
        _replace_keyword_args(keyword, tuple(censored_args))

    for end_logger in LOGGER.end_loggers:
        end_logger.end_keyword(keyword)

    # if not LOGGER._started_keywords:
    LOGGER.log_message = LOGGER.message

    if apply_filter:
        _replace_keyword_args(keyword, tuple(original_args))
        b = BuiltIn()
        # Return previous log level
        b.set_log_level(LOG_LEVEL)
        if DEBUGFILE_LOG_MSG_FN:
            LOGGER._other_loggers[0].log_message = DEBUGFILE_LOG_MSG_FN

@end_body_item
def _filtered_end_library_keyword(self, data: Keyword, implementation: Keyword, result: Keyword) -> None:
    """Modify Robot FW 7+ internal function "end_library_keyword".

    This function removes secret data from "end library keyword"
    logs and returns previous log level.
    """
    # pylint: disable=protected-access
    apply_filter = result.name in FILTERED_KEYWORDS
    original_args = result.args
    if apply_filter:
        censored_args = _hide_keyword_arg_values(result)
        _hide_keyword_arg_values(data)
        _replace_keyword_args(result, tuple(censored_args))
        _replace_keyword_args(data, tuple(censored_args))

    for end_logger in self.end_loggers:
        end_logger.end_library_keyword(data, implementation, result)

    if apply_filter:
        _replace_keyword_args(data, tuple(original_args))
        _replace_keyword_args(result, tuple(original_args))
        for other in self._other_loggers:
            for stored in OTHER_LOGGERS:
                if other == stored[0]:
                    other.log_message = stored[1]
                    break


def add_filter(keyword_name: str, par_index: int, secret: Optional[str]) -> None:
    """Add keyword to secrets filtering.

    Keyword name is according to Robot FW name, i.e. text presentation
    of keyword function like "Type Secret".
    Parameter index defines the index number of function parameter which is
    filtered out. First parameter is 0.
    """
    FILTERED_KEYWORDS[keyword_name] = (par_index, secret)


# List of keyword names for which filtering of secret parameters is applied.
# Format: "keyword name": index of secret parameter
FILTERED_KEYWORDS: dict[str, Any] = {}
LOG_LEVEL = "INFO"

# list (logger object, log_message fn)
OTHER_LOGGERS: list[tuple[object, Callable]] = []

try:
    DEBUGFILE_LOG_MSG_FN = LOGGER._other_loggers[0].log_message  # pylint: disable=protected-access
except IndexError:
    DEBUGFILE_LOG_MSG_FN = False

# Monkey patch Robot FW methods
rfw_major_version = int(rfw_version().split(".")[0])
if rfw_major_version < 7:
    LOGGER.start_keyword = _filtered_start_keyword
    LOGGER.end_keyword = _filtered_end_keyword
else:
    LOGGER.start_library_keyword = _filtered_start_library_keyword.__get__(LOGGER)  # pylint: disable=no-value-for-parameter
    LOGGER.end_library_keyword = _filtered_end_library_keyword.__get__(LOGGER)  # pylint: disable=no-value-for-parameter
