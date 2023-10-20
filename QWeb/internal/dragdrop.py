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
from selenium.webdriver.remote.webelement import WebElement

from robot.api import logger
from QWeb.internal.text import get_text_using_anchor
from QWeb.internal import element, javascript, frame
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebValueError


@frame.all_frames
def get_draggable_element(text: str, index: Union[int, str],
                          anchor: str) -> Union[WebElement, list[WebElement]]:
    attribute_match = '[title^="{0}"][draggable="true"],[alt^="{0}"][draggable="true"],' \
                      '[tooltip^="{0}"][draggable="true"],' \
                      '[data-tooltip^="{0}"][draggable="true"],' \
                      '[data-icon^="{0}"][draggable="true"],' \
                      '[aria-label^="{0}"][draggable="true"],' \
                      '[title^="{0}"][class*="draggableCell"]'.format(text)
    web_elements = []
    matches: Optional[list[WebElement]] = []
    try:
        index = int(index) - 1
    except ValueError as e:
        raise QWebValueError('Index needs to be number') from e
    if text.startswith('xpath=') or text.startswith('//'):
        web_element = element.get_unique_element_by_xpath(text, index)
        if web_element:
            return web_element
        raise QWebElementNotFoundError('Draggable element not found by locator {}'.format(text))
    web_elements = javascript.execute_javascript(
        'return document.querySelectorAll(\'{}\')'.format(attribute_match))
    if web_elements:
        return web_elements[index]
    web_elements = javascript.execute_javascript(
        'return document.querySelectorAll(\'[draggable="true"]\')')
    if web_elements:
        matches = _find_matches(web_elements, text)
        if matches:
            return matches[index]
        if text == 'index':
            logger.warn('Text is not matching to any draggable element. Found {} '
                        'draggable elements. Using index..'.format(len(web_elements)))
            return web_elements[index]
    return get_text_using_anchor(text, anchor)


def _find_matches(web_elements: list[WebElement], text: str) -> Optional[list[WebElement]]:
    matches = []
    for elem in web_elements:
        if elem.text and text in elem.text:
            matches.append(elem)
    if matches:
        return matches
    return None
