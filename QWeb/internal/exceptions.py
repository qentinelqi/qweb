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

FATAL_MESSAGES: list[str] = [
    "Failed to decode response", "chrome not reachable", "window was already closed",
    "Unable to get browser", "session deleted", "0 tabs open"
]


class QWebException(Exception):
    """
    Base class for other QWebExceptions

    """


class QWebSearchingMode(QWebException):
    """Raise when Searching mode is on. Prevents kw
    to execute"""


class QWebInstanceDoesNotExistError(QWebException):
    """Raise when for example table instance is
    undefined while user tries to use it"""


class QWebStalingElementError(QWebException):
    """Raise when Element is staling."""


class QWebElementNotFoundError(QWebException):
    """Raise when Element is not found
    from document."""


class QWebValueError(QWebException):
    """Raise when there is mismatch between
    expected condition/value and real situation."""


class QWebDriverError(QWebException):
    """Raise when element is not enabled
    or whatever situation where webdriver prevents our
    preferred action."""


class QWebTimeoutError(QWebException):
    """Raise when running out of time, preferred action is still
    unfinished and no other exceptions exists."""


class QWebUnexpectedConditionError(QWebException):
    """Raise when expected condition is not true. This is
    used by actions decorators during an execution."""


class QWebInvalidElementStateError(QWebDriverError):
    """Raise if element is in disabled state when trying
    to trigger keyword action."""


class QWebValueMismatchError(QWebValueError):
    """ Raise if real value is different than
    expected value."""


class QWebFileNotFoundError(QWebValueError):
    """ Raise if reference file is missing. """


class QWebTextNotFoundError(QWebException):
    """Raise when ScrollTo KW does not find searched text."""


class QWebUnexpectedAlert(QWebException):
    """Raise when actions are blocked by an alert box"""


class QWebEnvironmentError(QWebException):
    """Raise when actions do not work because of a faulty environment."""


class QWebBrowserError(QWebException):
    """Raise when connection to browser has been lost / browser crashed etc."""


class QWebIconNotFoundError(QWebException):
    """Raise when picture/icon is not found with image recognition."""
