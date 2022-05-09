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
from typing import Union
from selenium.webdriver.common.alert import Alert

from QWeb.internal.exceptions import QWebDriverError
from QWeb.internal import browser, decorators


@decorators.timeout_decorator_for_actions
def close_alert(alert: Alert, action: str) -> None:
    if action.upper() == 'ACCEPT':
        alert.accept()
    elif action.upper() == 'DISMISS':
        alert.dismiss()
    elif action.upper() == 'NOTHING':
        return
    else:
        raise QWebDriverError(
            "Invalid alert action '{}'. Must be ACCEPT, DISMISS or LEAVE".format(action))


@decorators.timeout_decorator_for_actions
def wait_alert(timeout: Union[int, float, str]) -> Alert:  # pylint: disable=unused-argument
    driver = browser.get_current_browser()
    return driver.switch_to.alert


@decorators.timeout_decorator_for_actions
def type_alert(alert: Alert, text: str, timeout: Union[int, float, str]) -> None:  # pylint: disable=unused-argument
    alert.send_keys(text)
