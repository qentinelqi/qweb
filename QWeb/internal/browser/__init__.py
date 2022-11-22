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
from typing import Union, Optional
from selenium.webdriver.remote.webdriver import WebDriver

from QWeb.internal.exceptions import QWebDriverError, QWebValueError
# These mime types were retrieved from
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
MIME_TYPES = ("application/epub+zip;"
              "application/java-archive;"
              "application/javascript;"
              "application/json;"
              "application/msword;"
              "application/octet-stream;"
              "application/octet-stream;"
              "application/ogg;"
              "application/pdf;"
              "application/rtf;"
              "application/typescript;"
              "application/vnd.amazon.ebook;"
              "application/vnd.apple.installer+xml;"
              "application/vnd.mozilla.xul+xml;"
              "application/vnd.ms-excel;"
              "application/vnd.ms-fontobject;"
              "application/vnd.ms-powerpoint;"
              "application/vnd.oasis.opendocument.text;"
              "application/vnd.oasis.opendocument;"
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;"
              "application/vnd.visio;"
              "application/x-7z-compressed"
              "application/x-abiword;"
              "application/x-bzip2;"
              "application/x-bzip;"
              "application/x-csh;"
              "application/x-rar-compressed;"
              "application/x-sh;"
              "application/x-shockwave-flash;"
              "application/x-tar;"
              "application/xhtml+xml;"
              "application/xml;"
              "application/zip;"
              "audio/aac;"
              "audio/midi;"
              "audio/ogg;"
              "audio/webm;"
              "audio/x-wav;"
              "font/otf;"
              "font/ttf;"
              "font/woff2;"
              "font/woff;"
              "image/gif;"
              "image/jpeg;"
              "image/png;"
              "image/svg+xml;"
              "image/tiff;"
              "image/webp;"
              "image/x-icon;"
              "text/calendar;"
              "text/css;"
              "text/csv;"
              "text/html;"
              "text/plain;"
              "video/3gpp2audio/3gpp2;"
              "video/3gppaudio/3gpp;"
              "video/mpeg;"
              "video/ogg;"
              "video/webm;"
              "video/x-msvideo")

_current_browser: Optional[WebDriver] = None
_open_browsers: list[WebDriver] = []


def get_current_browser() -> WebDriver:
    if _current_browser is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword"
                              " to open browser first")
    return _current_browser


def set_current_browser(index: Union[int, str]) -> None:
    # pylint: disable=global-statement
    global _current_browser

    if str(index).isdigit():
        if int(index) == 0:
            raise QWebValueError('SwitchBrowser index starts at 1.')

        i = int(index) - 1

        if i < len(_open_browsers):
            _current_browser = _open_browsers[i]
        else:
            raise QWebDriverError(f'Tried to select browser with index {index} but there are \
                                  {len(_open_browsers)} browsers open')
    elif str(index) == "NEW":
        _current_browser = _open_browsers[-1]
    else:
        raise QWebValueError('Given argument "{}" is not a digit or NEW'.format(index))


def get_open_browsers() -> list[WebDriver]:
    return _open_browsers


def cache_browser(driver: WebDriver) -> None:
    # pylint: disable=global-statement
    global _current_browser
    # pylint: disable=global-statement, global-variable-not-assigned
    global _open_browsers
    _current_browser = driver
    _open_browsers.append(driver)


def remove_from_browser_cache(driver: WebDriver) -> None:
    ''' Removes specific entry from browser cache.
    Control is moved to previously opened browser'''
    # pylint: disable=global-statement
    global _current_browser
    # pylint: disable=global-statement, global-variable-not-assigned
    global _open_browsers
    _open_browsers.remove(driver)
    # there's at least one browser open, move to latest
    _current_browser = _open_browsers[-1] if _open_browsers else None


def clear_browser_cache() -> None:
    ''' Removes all entries from browser cache. Used before quitting'''
    # pylint: disable=global-statement
    global _current_browser
    # pylint: disable=global-statement
    global _open_browsers
    _current_browser = None
    _open_browsers = []
