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
from selenium.common.exceptions import JavascriptException, StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from robot.api import logger
from QWeb.internal import javascript
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.exceptions import QWebStalingElementError
from QWeb.internal.page_node import PageNode


def check_frames(driver: WebDriver, **kwargs) -> list[Any]:
    visible_frames: list[WebElement] = []
    frames = javascript.execute_javascript('return document.querySelectorAll("iframe, frame")')
    if not frames:
        frames = []
    try:
        located = javascript.find_elements_by_xpath(driver, "//iframe|//frame")
        # A shadow frame comes back as a handle. switch_to.frame needs the
        # frame's name, which is added after the visibility check.
        frames += [item for item in located if not isinstance(item, PageNode)]
    except (QWebStalingElementError, StaleElementReferenceException) as error:
        # An unwrappable synthetic-shadow node makes the driver reject the whole
        # frame list. The querySelectorAll result above is still usable.
        logger.debug("Frame xpath search skipped: {}".format(error))
    shadow_dom = CONFIG["ShadowDOM"]
    if shadow_dom:
        shadow_frames = javascript.get_all_frames_from_shadow_dom()
        frames = list(dict.fromkeys(list(frames) + shadow_frames))
    frames = list(dict.fromkeys(frames))
    visible_only = kwargs.get("visibility", True)
    if not visible_only:
        return frames
    try:
        frames_obj = javascript.get_visibility(frames)
    except (
        StaleElementReferenceException,
        JavascriptException,
        QWebStalingElementError,
        TypeError,
    ) as error:
        # One frame the driver cannot measure must not skip the rest of the page.
        logger.debug("Frame visibility check skipped: {}".format(error))
        return frames
    if not frames_obj:
        return frames
    for frame, info in zip(frames, frames_obj):
        offset = info.get("offset")
        if offset:
            visible_frames.append(frame)
    if visible_frames:
        logger.debug("Found {} visible frames".format(len(visible_frames)))
        return visible_frames
    return frames
