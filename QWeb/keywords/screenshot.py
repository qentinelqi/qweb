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

from typing import Optional
from QWeb.internal import screenshot
from QWeb.internal.config_defaults import CONFIG
from robot.api import logger
from robot.api.deco import keyword


def verify_app(imagename: str) -> None:
    """Compare image to a known good one.

    :param imagename:
    :return:
    """
    status = screenshot.compare_screenshots(imagename, CONFIG["VerifyAppAccuracy"])
    if status is False:
        raise Exception('Images differ')


@keyword(tags=["Logging"])
def log_screenshot(filename: str = 'screenshot_{}.png', fullpage: bool = False) -> Optional[str]:
    r"""Log screenshot to Robot Framework log.

    Examples
    --------
    .. code-block:: robotframework

       LogScreenshot
       ${file}=     LogScreenshot  # returns full path to saved image file

    Parameters
    ----------
    filename : str
        Filename where the screenshot is saved.

        Note: if given filename exceeds operating system's limit for a filename length
        (usually 255 characters), this keyword will fail.

    fullpage : str
        | Capture full page screenshot instead of visible area only (if browser/driver supports it).
        | Currently supported in Firefox and Chromium based browsers (Chrome/Edge).
        | Default: False (visible area only)

    Returns
    -------
    filepath : full path to saved screenshot

    Related keywords
    ----------------
    \`LogPage\`
    """
    filepath: Optional[str] = None
    if CONFIG["LogScreenshot"]:
        screenshot_type = CONFIG["ScreenshotType"]
        if screenshot_type == 'screenshot':
            filepath = screenshot.save_screenshot(filename, fullpage=fullpage)
            screenshot.log_screenshot_file(filepath)
        elif screenshot_type == 'html':
            screenshot.log_html()
        elif screenshot_type == 'all':
            filepath = screenshot.save_screenshot(filename, fullpage=fullpage)
            screenshot.log_screenshot_file(filepath)
            screenshot.log_html()
        else:
            raise ValueError('Unknown screenshot type: {}'.format(screenshot_type))
    else:
        logger.info('Screenshots have been disabled with the SetConfig keyword.')

    return filepath
