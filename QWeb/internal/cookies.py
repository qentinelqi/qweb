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
from typing import Any
from QWeb.internal import browser
from selenium.common.exceptions import NoSuchWindowException


def delete_all_cookies() -> None:
    driver = browser.get_current_browser()
    if driver is None:
        raise NoSuchWindowException("Can't delete cookies, no open browser")
    driver.delete_all_cookies()


def get_cookies() -> list[dict[str, Any]]:
    driver = browser.get_current_browser()
    if driver is None:
        raise NoSuchWindowException("Can't list cookies, no open browser")
    return driver.get_cookies()
