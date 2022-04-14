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
from QWeb.internal import browser, text, util
from QWeb.internal.exceptions import QWebDriverError
from QWeb.internal.browser.safari import open_windows
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from robot.api import logger
import time


def get_window_handles() -> list[str]:
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword"
                              " to open browser first")
    return open_windows if util.is_safari() else driver.window_handles


def get_current_window_handle() -> str:
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword"
                              " to open browser first")
    return driver.current_window_handle


def append_new_windows_safari() -> None:
    """ Safari returns window handles in random order.
        We must keep track of opened windows in safari.
        This function will append new open windows to global list."""
    driver = browser.get_current_browser()
    all_handles = driver.window_handles
    for i in all_handles:
        if i not in open_windows:
            open_windows.append(i)


def get_url() -> str:
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword"
                              " to open browser first")
    return driver.current_url


def switch_to_window(handle) -> None:
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword"
                              " to open browser first")
    driver.switch_to.window(handle)


def swipe(direction: str, times: Union[str, int] = '1', start: Optional[str] = None) -> None:
    """
    Internal swipe function used by the swipe keywords. Uses the arrow keys to "swipe",
    unless a starting point is given. If a starting point is given, drag and drop is used.
    Functionality isn't 100% same as in QMobile, but this should work in most cases.
    """
    logger.info('Even though the keyword is called swipe, '
                'it actually uses arrow keys or drag and drop to "swipe".')
    directions = {
        'down': (Keys.ARROW_DOWN, 0, 500),
        'up': (Keys.ARROW_UP, 0, -500),
        'left': (Keys.ARROW_LEFT, -500, 0),
        'right': (Keys.ARROW_RIGHT, 500, 0)
    }
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword"
                              " to open browser first")
    action_chains = ActionChains(driver)
    try:
        times = int(times)
    except ValueError as e:
        raise ValueError('Amount of times swiped needs to be an integer.') from e
    if not start:
        default_swipe_length = 20
        times = default_swipe_length * times
        for _ in range(int(times)):
            action_chains.send_keys(directions[direction][0])
            action_chains.pause(0.05)
        action_chains.perform()
        time.sleep(.5)
    else:
        start_element = text.get_unique_text_element(start)
        action_chains.click(start_element)
        action_chains.pause(.5)
        action_chains.drag_and_drop_by_offset(start_element, directions[direction][1] * times,
                                              directions[direction][2] * times)
        action_chains.perform()
        time.sleep(.5)
