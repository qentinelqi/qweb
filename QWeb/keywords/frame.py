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
"""Keywords for webpage and frame elements.

Frame is considered to be an element in a webapage which can contain another
webpage. Usually these elements have iframe -tag.
"""
from __future__ import print_function

from selenium.common.exceptions import NoSuchFrameException

from robot.api.deco import keyword

from QWeb.internal import browser, element, frame, javascript


@keyword(tags=["Config"])
def use_frame(locator: str) -> None:
    """Make following keywords to use frame on a page.

    Examples
    --------
    .. code-block:: robotframework

        UseFrame    //iframe

    Parameters
    ----------
    locator : str
        Xpath expression without xpath= prefix or index (first = 1 etc.)

    Raises
    ------
    NoSuchFrameException
        If the frame is not found
    """
    frame.wait_page_loaded()
    try:
        index = int(locator) - 1
        webelement = javascript.execute_javascript(
            'document.querySelectorAll("iframe, frame")[{}]'.format(index))
    except ValueError:
        webelement = element.get_unique_element_by_xpath(locator)
    driver = browser.get_current_browser()
    try:
        driver.switch_to.frame(webelement)
    except NoSuchFrameException as e:
        raise NoSuchFrameException('No frame wound with xpath: {0}'.format(locator)) from e


@keyword(tags=["Config"])
def use_page() -> None:
    """Make following keywords to use the page and not a frame on a page.

    Examples
    --------
    .. code-block:: robotframework

       UsePage

    """
    frame.wait_page_loaded()
    driver = browser.get_current_browser()
    driver.switch_to.default_content()


@keyword(tags=("Browser", "Interaction"))
def refresh_page() -> None:
    r"""Refresh the current window.

    Examples
    --------
    .. code-block:: robotframework

       RefreshPage

    Related keywords
    ----------------
    \`Back\`, \`GoTo\`, \`MaximizeWindow\`
    """
    frame.wait_page_loaded()
    driver = browser.get_current_browser()
    driver.refresh()


@keyword(tags=("Browser", "Interaction"))
def back() -> None:
    r"""Navigates back in the current window.

    Examples
    --------
    .. code-block:: robotframework

       Back

    Related keywords
    ----------------
    \`Forward\`, \`GoTo\`, \`RefreshPage\`, \`MaximizeWindow\`


    """
    frame.wait_page_loaded()
    driver = browser.get_current_browser()
    driver.back()


@keyword(tags=("Browser", "Interaction", "Window"))
def forward() -> None:
    r"""Navigates forward in the current window.

    Examples
    --------
    .. code-block:: robotframework

       Forward

    Related keywords
    ----------------
    \`Back\`, \`GoTo\`, \`RefreshPage\`, \`MaximizeWindow\`


    """
    frame.wait_page_loaded()
    driver = browser.get_current_browser()
    driver.forward()


@keyword(tags=["Logging"])
def log_page() -> None:
    r"""Save and log current html.

    The html content is saved as html file in the same folder where log is.
    The current page and the link to it are represented in the log in
    iframe so it one can see the page as it was.

    Examples
    --------
    .. code-block:: robotframework

       LogPage

    Note
    ----
    Does not handle frames.

    Todo
    ----
    Replace relative paths in the src and href attributes. This way we get
    css properties and icons.

    Related keywords
    ----------------
    \`LogScreenshot\`
    """
    raw_html = frame.get_raw_html()
    output_dir = frame.get_output_dir()
    html_source_count = frame.get_html_source_count()
    filepath = frame.save_source(raw_html, output_dir, html_source_count)
    frame.link_source_to_log(html_source_count, filepath)
    html_source_count += 1
    frame.set_html_source_count(html_source_count)
