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
""" Robot framework secrets handling.

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
from typing import Any, Optional
from robot.model.keyword import Keyword

from robot.output.logger import LOGGER
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
    if hasattr(keyword.result, 'args'):
        setattr(keyword.result, 'args', args)
    if hasattr(keyword.data, 'args'):
        setattr(keyword.data, 'args', args)


def _hide_keyword_arg_values(keyword: Keyword) -> list[str]:
    par_index, secret = filtered_keywords[keyword.kwname]
    censored_args = list(keyword.args)
    if secret == 'hint':
        censored_args[par_index] = 'SECRET'
    else:
        censored_args[par_index] = "*" * 5

    return censored_args


def _filtered_start_keyword(keyword: Keyword) -> None:
    """Modify Robot FW internal function "start_keyword".

    This function removes secret data from "start keyword"
    logs and disables logging during the keyword.
    """
    # pylint: disable=protected-access, global-statement
    global log_level
    apply_filter = keyword.kwname in filtered_keywords
    original_args = keyword.args
    if apply_filter:
        censored_args = _hide_keyword_arg_values(keyword)
        _replace_keyword_args(keyword, tuple(censored_args))

    LOGGER._started_keywords += 1
    LOGGER.log_message = LOGGER._log_message
    for start_logger in LOGGER.start_loggers:
        start_logger.start_keyword(keyword)

    if apply_filter:
        _replace_keyword_args(keyword, tuple(original_args))
        b = BuiltIn()
        # Disable logging and store previous log level
        if 'INFO' not in b.get_variables()['${LOG_LEVEL}']:
            log_level = b.set_log_level("INFO")
        if debugfile_log:
            LOGGER._other_loggers[0].log_message = lambda x: None


def _filtered_end_keyword(keyword: Keyword) -> None:
    """Modify Robot FW internal function "end_keyword".

    This function removes secret data from "end keyword"
    logs and returns previous log level.
    """
    # pylint: disable=protected-access, global-statement
    apply_filter = keyword.kwname in filtered_keywords
    original_args = keyword.args
    if apply_filter:
        censored_args = _hide_keyword_arg_values(keyword)
        _replace_keyword_args(keyword, tuple(censored_args))

    LOGGER._started_keywords -= 1
    for end_logger in LOGGER.end_loggers:
        end_logger.end_keyword(keyword)

    if not LOGGER._started_keywords:
        LOGGER.log_message = LOGGER.message

    if apply_filter:
        _replace_keyword_args(keyword, tuple(original_args))
        b = BuiltIn()
        # Return previous log level
        b.set_log_level(log_level)
        if debugfile_log:
            LOGGER._other_loggers[0].log_message = debugfile_log


def add_filter(keyword_name: str, par_index: int, secret: Optional[str]) -> None:
    """Add keyword to secrets filtering.

    Keyword name is according to Robot FW name, i.e. text presentation
    of keyword function like "Type Secret".
    Parameter index defines the index number of function parameter which is
    filtered out. First parameter is 0.
    """
    filtered_keywords[keyword_name] = (par_index, secret)


# List of keyword names for which filtering of secret parameters is applied.
# Format: "keyword name": index of secret parameter
filtered_keywords: dict[str, Any] = {}
log_level = "INFO"

try:
    debugfile_log = LOGGER._other_loggers[0].log_message  # pylint: disable=protected-access
except IndexError:
    debugfile_log = False

# Monkey patch Robot FW methods
LOGGER.start_keyword = _filtered_start_keyword
LOGGER.end_keyword = _filtered_end_keyword
