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
from numpy import ndarray

import base64
import json
import os
from uuid import uuid4

import cv2
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import UnexpectedAlertPresentException, \
                                       WebDriverException, InvalidSessionIdException
from QWeb.internal.browser import firefox, chrome, edge
from QWeb.internal.exceptions import QWebDriverError
from QWeb.internal import browser
from QWeb.keywords import config
from skimage.metrics import structural_similarity
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.utils import get_link_path
from pyautogui import screenshot as pyscreenshot
from tempfile import gettempdir

SCREEN_SHOT_DIR_NAME = 'screenshots'
VERIFYAPP_DIR_NAME = 'verifyapp'
VALID_FILENAME_CHARS = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
MAX_LENGTH = 100  # filenames longer than 255 are not allowed by os


def _create_screenshot_folder(foldername: str) -> str:
    try:
        robot_output = BuiltIn().get_variable_value('${OUTPUT DIR}')
        screen_shot_dir = os.path.join(robot_output, foldername)
    except RobotNotRunningError:
        screen_shot_dir = os.path.join(os.getcwd(), foldername)

    if not os.access(screen_shot_dir, os.W_OK):
        screen_shot_dir = os.path.join(gettempdir(), foldername)

    if not os.path.isdir(screen_shot_dir):
        os.makedirs(screen_shot_dir)

    return screen_shot_dir


def _remove_invalid_chars(text_to_check: str) -> str:
    """
    Removes invalid characters from filename
    :param text_to_check:
    :return:
    """
    valid = "".join(c for c in text_to_check if c in VALID_FILENAME_CHARS)
    return valid if len(valid) <= MAX_LENGTH else valid[:MAX_LENGTH - 1]


def compare_screenshots(filename: str, accuracy: Union[str, float]) -> bool:
    # pylint: disable=no-member
    """Compare screenshot against reference, take reference if missing.

    :param filename:
    :return:
    """
    screenshot_dir = _create_screenshot_folder(SCREEN_SHOT_DIR_NAME)
    verifyapp_dir = _create_screenshot_folder(VERIFYAPP_DIR_NAME)
    test_name = BuiltIn().get_variable_value('${TEST NAME}')
    filename = _remove_invalid_chars('{0}_{1}'.format(test_name, filename))
    filename = filename.replace(" ", "_")
    filename_ref = '{}_ref.png'.format(filename)
    filename_cmp = '{}.png'.format(filename)
    filename_dif = '{}_dif.png'.format(filename)
    try:
        accuracy = float(accuracy)
    except ValueError as e:
        raise ValueError('Invalid accuracy: {}'.format(accuracy)) from e
    # Save reference screenshot if it does not exist
    if not os.path.isfile(os.path.join(verifyapp_dir, filename_ref)):
        filepath_ref = save_screenshot(filename_ref, VERIFYAPP_DIR_NAME)

        logger.info('Reference screenshot missing, saving.')
        logger.info('Image path: {}'.format(filename_ref))
        log_screenshot_file(filepath_ref)
        status = True
    # Compare screenshots if reference exists
    else:
        filepath_ref = os.path.join(verifyapp_dir, filename_ref)
        filepath_cmp = save_screenshot(filename_cmp, SCREEN_SHOT_DIR_NAME)
        ref_image = cv2.imread(filepath_ref, cv2.IMREAD_GRAYSCALE)
        ref_image_c = cv2.imread(filepath_ref, cv2.IMREAD_COLOR)
        new_image = cv2.imread(filepath_cmp, cv2.IMREAD_GRAYSCALE)

        (score, diff) = structural_similarity(ref_image, new_image, full=True)
        if score > accuracy:
            logger.info('Images match with score: {}'.format(score))
            log_screenshot_file(filepath_cmp)
            logger.info('Image path: {}'.format(filename_cmp))
            status = True
        else:
            logger.error('Images differ with score: {}'.format(score))
            logger.info('Reference image: {}'.format(filename_ref))
            log_screenshot_file(filepath_ref)
            logger.info('Comparison image: {}'.format(filename_cmp))
            ref_image_c = _draw_contours(diff, ref_image_c)

            log_screenshot_file(filepath_cmp)

            filepath_dif = os.path.join(screenshot_dir, filename_dif)
            cv2.imwrite(filepath_dif, ref_image_c)
            logger.info('Difference image: {}'.format(filename_dif))
            log_screenshot_file(filepath_dif)
            status = False
    return status


def _draw_contours(diff: ndarray, ref_image_c: ndarray) -> ndarray:
    # pylint: disable=no-member
    """Draw contours on ref_image_c based on diff

    :param diff:
    :param ref_image_c:
    :return:
    """
    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 220, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # api differs on opencv3 and opencv4
    index = 1 if cv2.__version__.startswith("3") else 0  # type: ignore

    for c in contours[index]:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(ref_image_c, (x, y), ((x + w), (y + h)), (0, 0, 255), 2)
    return ref_image_c


# pylint: disable=too-many-branches
def save_screenshot(filename: str = 'screenshot_{}.png',
                    folder: str = SCREEN_SHOT_DIR_NAME,
                    pyautog: bool = False,
                    fullpage: bool = False) -> str:
    """Save screenshot of web page to a file.

    If robot framework is running then screenshots are saved to
    ${OUTPUT DIR}/screenshots. Otherwise the file is saved to current working
    directory. If there is no write access to cwd (jupyter in windows for example seems set cwd to
    system32) screenshot dir is set to operating systems temp directory.

    Parameters
    ----------
    filename : str (default 'screenshot_{}.png')
        filename where the screenshot will be saved. Note: Will fail if given filename
        exceeds operating system's limit for a filename (usually 255 characters).
    folder : str (default SCREEN_SHOT_DIR_NAME)
        folder where screenshot will be saved
    pyautog : bool (default False)
        True if pyautogui shall be used for screenshots and
        False if selenium shall be used

    Returns
    -------
    str
        Filepath to the saved file.
    """
    test_name = None
    try:
        robot_output = BuiltIn().get_variable_value('${OUTPUT DIR}')
        test_name = BuiltIn().get_variable_value('${TEST NAME}')
        screen_shot_dir = os.path.join(robot_output, folder)

    except RobotNotRunningError:
        screen_shot_dir = os.path.join(os.getcwd(), folder)

        if not os.access(screen_shot_dir, os.W_OK):
            screen_shot_dir = os.path.join(gettempdir(), folder)

    if not os.path.isdir(screen_shot_dir):
        os.makedirs(screen_shot_dir)

    if filename == 'screenshot_{}.png' and test_name is None:
        filename = filename.format(uuid4())

    elif filename == 'screenshot_{}.png':
        name_with_underscores = str(test_name).replace(" ", "_")
        valid_name = _remove_invalid_chars(name_with_underscores)
        filename = "screenshot-" + valid_name + "-{}".format(uuid4()) + '.png'

    filepath = os.path.join(screen_shot_dir, filename)

    try:
        driver = browser.get_current_browser()
    except QWebDriverError:
        driver = None
        config.set_config("OSScreenshots", True)

    if pyautog is True or config.get_config("OSScreenshots"):
        # try to remove image, needed for scrot > 0.9
        try:
            os.remove(filepath)
        except OSError:
            pass

        pyscreenshot(filepath)
        logger.info('Saved screenshot to {}'.format(filepath))
        return filepath

    if driver:
        saved: Union[str, bool]
        try:
            browser_name = driver.capabilities['browserName']
            if not fullpage:
                saved = driver.save_screenshot(filepath)
            else:
                saved = full_page_screenshot(driver, filepath, browser_name)

        except (UnexpectedAlertPresentException, WebDriverException, QWebDriverError,
                InvalidSessionIdException):
            saved = pyscreenshot(filepath)
        if not saved:
            raise ValueError(f'Saving screenshot to {filepath} did not succeed.')

    logger.info('Saved screenshot to {}'.format(filepath))
    return filepath


def log_screenshot_file(filepath: str) -> None:
    """Log screenshot file to robot framework log.

    Uses robot.utils.get_link_path to determine the relative path to the robot
    framework log file.

    Parameters
    ----------
    filepath : str
        Filepath to the screenshot file.
    """
    try:
        robot_output = BuiltIn().get_variable_value('${OUTPUT DIR}')
        if not config.get_config("OSScreenshots"):
            logger.info('Current url is: {}'.format(get_url()))
        link = get_link_path(filepath, robot_output)
        logger.info('<a href="{0}"><img src="{0}" width="800px"></a>'.format(link), html=True)

    except RobotNotRunningError:
        return


def log_html() -> None:
    source_html_counter = 1
    url = get_url()
    logger.info('Current url: {}'.format(url))
    raw_html = get_source()
    log_dir = BuiltIn().get_variable_value('${OUTPUT DIR}')
    filename = "source_{}.html".format(uuid4())
    filepath = os.path.join(log_dir, 'screenshots', filename)
    with open(filepath, 'w', encoding="utf-8") as htmlfile:
        htmlfile.write(raw_html)
    logger.info(r'''<a id="source_link_{0}">{1}</a></br>
    <iframe id="source_{0}" width="1220px", height="650px"></iframe>
    <script type="text/javascript">
    element = document.getElementById("source_link_{0}");
    element.setAttribute("href", "{2}");
    document.getElementById("source_{0}").setAttribute("src", "{1}");
    </script>'''.format(source_html_counter, 'screenshots/' + filename,
                        filepath.replace("\\", "\\\\")),
                html=True)
    source_html_counter += 1


def get_url() -> Optional[str]:
    try:
        driver = browser.get_current_browser()
        return driver.current_url
    except QWebDriverError:
        logger.warn('Could not take a screenshot of browser because it is not open.')
        return None


def get_source() -> str:
    driver = browser.get_current_browser()
    return driver.page_source


def chromium_full_screenshot(driver: WebDriver, filepath: str) -> str:

    def send(cmd, params):
        resource = f"/session/{driver.session_id}/chromium/send_command_and_get_result"

        # pylint:disable=W0212
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')

    def evaluate(script):
        response = send('Runtime.evaluate', {'returnByValue': True, 'expression': script})
        return response['result']['value']

    metrics = evaluate("({"
                       "width: Math.max(window.innerWidth, "
                       "document.body.scrollWidth, "
                       "document.documentElement.scrollWidth)|0,"
                       "height: Math.max(window.innerHeight, document.body.scrollHeight, "
                       "document.documentElement.scrollHeight)|0,"
                       "deviceScaleFactor: window.devicePixelRatio || 1,"
                       "mobile: typeof window.orientation !== 'undefined'"
                       "})")
    send('Emulation.setDeviceMetricsOverride', metrics)
    screenshot = send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})
    send('Emulation.clearDeviceMetricsOverride', {})

    image = base64.b64decode(screenshot['data'])
    with open(filepath, 'wb') as f:
        f.write(image)

    return filepath


def full_page_screenshot(driver: WebDriver, filepath: str, browser_name: str) -> str:
    if browser_name in firefox.NAMES:
        saved = driver.get_full_page_screenshot_as_file(filepath)  # type: ignore
    elif browser_name in chrome.NAMES or browser_name in edge.NAMES:
        saved = chromium_full_screenshot(driver, filepath)
    else:
        logger.warn("Your current browser does not support full page screenshots")
        saved = save_screenshot(filepath, fullpage=False)

    return saved
