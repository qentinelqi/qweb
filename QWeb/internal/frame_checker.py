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
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from robot.api import logger
from QWeb.internal import javascript
from QWeb.internal.config_defaults import CONFIG


def check_frames(driver: WebDriver, **kwargs) -> list[WebElement]:
    visible_frames: list[WebElement] = []
    frames = javascript.execute_javascript('return document.querySelectorAll("iframe, frame")')
    if not frames:
        frames = []
    frames += driver.find_elements(By.XPATH, "//iframe|//frame")
    shadow_dom = CONFIG['ShadowDOM']
    if shadow_dom:
        frames = javascript.get_all_frames_from_shadow_dom()
    visible_only = kwargs.get('visibility', True)
    if not visible_only:
        return frames
    frames_obj = javascript.get_visibility(list(dict.fromkeys(frames)))
    if not frames_obj:
        return frames
    for frame in frames_obj:
        offset = frame.get('offset')
        if offset:
            visible_frames.append(frame.get('elem'))  # type: ignore
    if visible_frames:
        logger.debug('Found {} visible frames'.format(len(visible_frames)))
    return visible_frames
