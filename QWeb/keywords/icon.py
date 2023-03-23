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
from typing import Union, Optional

import pyautogui
from selenium.webdriver.remote.webelement import WebElement
from QWeb.internal import icon, decorators, screenshot, util, text, element
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebIconNotFoundError
from QWeb.internal.config_defaults import CONFIG
from PIL import Image
from robot.api import logger
from robot.api.deco import keyword
import io
import os


@keyword(tags=("Icon", "Interaction"))
@decorators.timeout_decorator
def click_icon(image: str,
               template_res_w: Optional[int] = None,
               browser_res_w: Optional[int] = None,
               timeout: Union[int, float, str] = 0) -> None:  # pylint: disable=unused-argument
    r"""Click the icon on the screen.

    In case you want to click icons you always have to have reference images.

    If reference picture are not in default folders (images, files, downloads) then
    BASE_IMAGE_PATH should be defined in a robot file before using this keyword

    Examples
    --------
    .. code-block:: robotframework

        *** Variables ***
        ${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}resources${/}images

    BASE_IMAGE_PATH should lead to the folder where all your reference icons are

    .. code-block:: robotframework

        ClickIcon                   plane

    Related keywords
    ----------------
    \`ClickCell\`, \`ClickCheckbox\`, \`ClickElement\`,
    \`ClickItem\`, \`ClickList\`, \`ClickText\`,
    \`ClickUntil\`, \`ClickWhile\`, \`VerifyIcon\`
    """
    if not browser_res_w:
        browser_res_w = util.get_monitor_width()  # pyautogui works on whole screen

    # use current resolution by default
    if not template_res_w:
        template_res_w = browser_res_w

    template_res_w, browser_res_w = int(template_res_w), int(browser_res_w)
    image_path = icon.get_full_image_path(image)
    x, y = icon.image_recognition(str(image_path), template_res_w, browser_res_w, pyautog=True)
    if x == -1:
        raise QWebElementNotFoundError("Couldn't find the icon from the screen")
    if CONFIG.get_value("RetinaDisplay"):
        x = int(x * 0.5)
        y = int(y * 0.5)
    pyautogui.moveTo(x, y)
    pyautogui.click(x, y)


@keyword(tags=("Icon", "Verification"))
def is_icon(
    image: str,
    template_res_w: Optional[int] = None,
    browser_res_w: Optional[int] = None,
) -> bool:
    r"""Check is the icon on the screen.

    In case you want to use this keyword you always have to have reference images.
    If reference image are not in default folders (images, files, downloads) then
    BASE_IMAGE_PATH should be defined in a robot file before using this keyword.

    Examples
    --------
    .. code-block:: robotframework

        *** Variables ***
        ${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}resources${/}images

    BASE_IMAGE_PATH should lead to the folder where all your reference icons are

    .. code-block:: robotframework

        ${status}                   IsIcon                   plane

    ${status} will be True or False.

    Related keywords
    ----------------
    \`CaptureIcon\`, \`ClickIcon\`, \`VerifyIcon\`
    """
    if not browser_res_w:
        browser_res_w = util.get_browser_width()

    # use current resolution by default
    if not template_res_w:
        template_res_w = browser_res_w

    template_res_w, browser_res_w = int(template_res_w), int(browser_res_w)
    image_path = icon.get_full_image_path(image)
    x, _y = icon.image_recognition(str(image_path), template_res_w, browser_res_w, pyautog=False)

    if x == -1:
        return False
    return True


@keyword(tags=("Icon", "Verification"))
@decorators.timeout_decorator
def verify_icon(
        image: str,
        template_res_w: Optional[int] = None,
        browser_res_w: Optional[int] = None,
        timeout: Union[int, float, str] = 0  # pylint: disable=unused-argument
) -> bool:
    r"""Verify page contains icon.

    In case you want to use this keyword you always have to have reference images.
    If reference image are not in default folders (images, files, downloads) then
    BASE_IMAGE_PATH should be defined in a robot file before using this keyword.
    LogMatchedIcons configuration is used to log screenshots of matched images
    to logs. By default matched images are not logged.

    Examples
    --------
    .. code-block:: robotframework

        *** Variables ***
        ${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}resources${/}images

    BASE_IMAGE_PATH should lead to the folder where all your reference icons are

    .. code-block:: robotframework

        SetConfig                    LogMatchedIcons    True  # Log matched image to logsß
        VerifyIcon                   plane

    Parameters
    ----------
    image : str
        Image name with or without extension
    template_res_w : int
        Reference image resolution / width. 1920 by default and
        image will be scaled to most common resolutions.
    browser_res_w : int
        Browser resolution / width. None (default) indicates
        that QWeb will figure out current browser width.
    timeout : int
        How long we try to find the element for.

    Related keywords
    ----------------
    \`CaptureIcon\`, \`ClickIcon\`, \`IsIcon\`
    """
    if not browser_res_w:
        browser_res_w = util.get_browser_width()

    # use current resolution by default
    if not template_res_w:
        template_res_w = browser_res_w

    template_res_w, browser_res_w = int(template_res_w), int(browser_res_w)

    image_path = icon.get_full_image_path(image)
    x, _y = icon.image_recognition(str(image_path), template_res_w, browser_res_w, pyautog=False)
    if x == -1:
        raise QWebIconNotFoundError("Couldn't find the icon from the screen")
    return True


@keyword(tags=("Icon", "Interaction"))
@decorators.timeout_decorator
def capture_icon(
        locator: str,
        folder: str = 'screenshots',
        filename: str = 'screenshot_{}.png',
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        **kwargs) -> Optional[str]:  # pylint: disable=unused-argument
    r"""Take a screenshot of an element.

    Examples
    --------
    .. code-block:: robotframework

        ${some_xpath}=       //*[@value\="Button3"]
        CaptureIcon          ${some_xpath}

        CaptureIcon          Button3
        CaptureIcon          Button3    filename=custom_screenshot_name_123.png
        CaptureIcon          Button3    C:/custom/folder/path   custom_screenshot_name_123.png

    Parameters
    ----------
    locator : str
        Locator for the element we are trying to capture, XPath or attribute value. When using
        XPaths, the equal sign "=" must be escaped with a "\\".
    folder : str
        Optional folder path. Default value is the screenshots folder.
    filename : str
        Optional filename.
    timeout : int
        How long we try to find the element for.

    Returns
    -------
    filepath : full path to saved screenshot

    Related keywords
    ----------------
    \`ClickIcon\`, \`IsIcon\`, \`VerifyIcon\`
    """
    web_element: Optional[WebElement]
    if util.xpath_validator(locator):
        web_element = element.get_unique_element_by_xpath(locator)
    else:
        web_element = text.get_item_using_anchor(locator, anchor='1', **kwargs)

    if web_element is not None:
        img = Image.open(io.BytesIO(web_element.screenshot_as_png))
        filepath = os.path.join(screenshot.save_screenshot(filename, folder))
        logger.info('Screenshot path: {}'.format(filepath.replace('\\', '/')), also_console=True)
        img.save(filepath)
        screenshot.log_screenshot_file(filepath)

    return filepath
