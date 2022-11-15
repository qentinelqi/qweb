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
"""Keywords for draggable elements."""
from __future__ import annotations
from typing import Union
from selenium.webdriver.remote.webelement import WebElement

import pyautogui
from robot.api import logger
from robot.api.deco import keyword
from robot.utils import timestr_to_secs as _timestr_to_secs
from QWeb.internal import element, decorators, dragdrop
from QWeb.internal import text as internal_text
from QWeb.internal import javascript


@keyword(tags=["Interaction"])
@decorators.timeout_decorator
def drag_drop(locator: str,
              target_locator: str,
              index: int = 1,
              anchor: str = "1",
              target_anchor: str = "1",
              timeout: Union[int, float, str] = 0,
              dragtime: Union[int, str] = '0.5s',
              left: int = 0,
              right: int = 0,
              above: int = 0,
              below: int = 0,
              loc_left: int = 0,
              loc_right: int = 0,
              loc_above: int = 0,
              loc_below: int = 0) -> None:
    # pylint: disable=unused-argument
    r"""Drag and drop element.

    Finds draggable element by it's visible text, tooltip attribute, index
    or xpath.
    Target element is found by it's visible text or xpath.

    Keyword tries to drag element to target element.
    Gets coordinates from WebDriver and uses pyautogui to simulate mouse
    actions based on those coordinates.

    Zoom level needs to be 100% in screen settings so that coordinates
    are matching with actual view. (Preferable resolution 1920x1080)

    Examples
    --------
    .. code-block:: robotframework

        DragDrop       draggable      target
        DragDrop       draggable      //*[@id="some_id"]
        DragDrop       index          Foo       index=3
        DragDrop       draggable      target    dragtime=2s
        DragDrop       draggable      target    right=5   below=2
        DragDrop       draggable      target    right=5   below=2   loc_above=40

    Parameters
    ----------
    locator : str
        Visible text, some element attribute(check ClickItem), xpath or
        text index to locate draggable element.
    target_locator : str
        Visible text or xpath to locate target element for draggable.
    index : int
        Index to point out right draggable if there is many or if
        there is no visible text/attribute which can be use to locate
        correct element.
    anchor : str
        In some cases(f.e Angular) element could be draggable even if
        draggable attribute doesn't exists. Then we are using traditional
        text match(check clicktext) to find correct
        element. Anchor can be index or some text near to draggable element.
        (default 1)
    target_anchor
        Text near the target element or index. If the page contains many
        places where the text argument is then anchor is used to get the
        one that is closest to it. (default 1)
    timeout : str | int
        How long we try to find elemenst before failing
    dragtime : str | int
        How long drag should take. Some applications need longer time
    left : int
       Offset how many pixels left of target center we drag
    right : int
       Offset how many pixels right of target center we drag
    above : int
       Offset how many pixels above of target center we drag
    below : int
       Offset how many pixels below of target center we drag
    loc_left : int
       Offset how many pixels left of locator center we start dragging
    loc_right : int
       Offset how many pixels right of locator center we start dragging
    loc_above : int
       Offset how many pixels above of locator center we start dragging
    loc_below : int
       Offset how many pixels below of locator center we start dragging

    Related keywords
    ----------------
    \`SwipeDown\`, \`SwipeLeft\`, \`SwipeRight\`, \`SwipeUp\`
    """
    pyautogui.FAILSAFE = False
    draggable = dragdrop.get_draggable_element(locator, index, anchor)
    if target_locator.startswith('xpath=') or target_locator.startswith('//'):
        target_elem = element.get_unique_element_by_xpath(target_locator, index=int(index - 1))
    else:
        target_elem = internal_text.get_text_using_anchor(target_locator, target_anchor)
    x, y = _get_coordinates(draggable)
    x = x + int(loc_right) - int(loc_left)
    y = y - int(loc_above) + int(loc_below)
    logger.debug('draggable x is {} and y is {}'.format(x, y))
    pyautogui.moveTo(x, y)
    x, y = _get_coordinates(target_elem)
    x = x + int(right) - int(left)
    y = y - int(above) + int(below)
    logger.debug('target x is {} and y is {}'.format(x, y))
    dragtime = _timestr_to_secs(dragtime)
    pyautogui.dragTo(x, y, dragtime, button='left')
    pyautogui.FAILSAFE = True


def _get_coordinates(web_element: WebElement) -> tuple[int, int]:
    x_diff = javascript.execute_javascript(
        'return window.outerWidth-window.innerWidth+screen.availLeft')
    y_diff = javascript.execute_javascript(
        'return window.outerHeight-window.innerHeight+screen.availTop')
    elem = javascript.execute_javascript("return arguments[0].getBoundingClientRect()", web_element)
    logger.debug("coords: {0}".format(elem))
    y = elem['y']

    x_coord = web_element.location['x'] + x_diff + web_element.size['width'] / 2
    y_coord = y + y_diff + web_element.size['height'] / 2
    return int(x_coord), int(y_coord)
