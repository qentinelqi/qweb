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
import importlib.resources
from typing import Any, Union
from selenium.webdriver.remote.webelement import WebElement
from QWeb.internal import browser


def load_js(filename):

    # Adjust the package path as needed
    return (importlib.resources.files('QWeb.internal.js')
            .joinpath(filename)
            .read_text(encoding='utf-8'))


# Preload JS files at import
_TOAST_NOTIFICATION_JS = load_js('toast_notification.js')
_GET_VISIBILITY_JS = load_js('get_visibility.js')
_HIGHLIGHT_ELEMENT_JS = load_js('highlight_element.js')
_GET_BY_ATTRIBUTES_JS = load_js('get_by_attributes.js')
_GET_CHILDNODES_JS = load_js('get_childnodes.js')
_GET_BY_LABEL_JS = load_js('get_by_label.js')
_GET_PARENT_LIST_JS = load_js('get_parent_list.js')
_FIND_TEXT_FROM_TEXTNODES_JS = load_js('find_text_from_textnodes.js')
_GET_CLICKABLE_JS = load_js('get_clickable.js')
_GET_RECURSIVE_WALK_JS = load_js('get_recursive_walk.js')
_GET_TEXT_ELEMENTS_FROM_SHADOW_DOM_JS = load_js('get_text_elements_from_shadow_dom.js')
_GET_CLICKABLE_FROM_SHADOW_DOM_JS = load_js('get_clickable_from_shadow_dom.js')
_GET_ALL_FRAMES_FROM_SHADOW_DOM_JS = load_js('get_all_frames_from_shadow_dom.js')
_GET_ALL_INPUT_ELEMENTS_FROM_SHADOW_DOM_JS = load_js('get_all_input_elements_from_shadow_dom.js')
_GET_ALL_DROPDOWN_ELEMENTS_FROM_SHADOW_DOM_JS = load_js('get_all_dropdown_elements_shadow_dom.js')
_GET_ITEM_ELEMENTS_FROM_SHADOW_DOM_JS = load_js('get_item_elements_from_shadow_dom.js')


def execute_javascript(script: str, *args) -> Any:
    """Run given javascript on current window.

    Parameters
    ----------
    script : str
        Javascript code.
    *args : WebElement
        WebElement object that is stored in to variable "arguments" which is
        an array in javascript. Check example.

    Returns
    -------
    str
        Output of the executed javascript.

    Example
    -------
    execute_javascript('arguments[0].setAttribute("style", "background-color:yellow")', web_element)
    """
    driver = browser.get_current_browser()
    return driver.execute_script(script, *args)


def get_visibility(web_elements: list[WebElement]) -> list[dict]:
    """Return web element objects (using external JS file, preloaded)."""
    js = _GET_VISIBILITY_JS
    return execute_javascript(js, web_elements)


def highlight_element(
    element: WebElement, draw_only: bool, flash_border: bool = False, color: str = "blue"
) -> None:
    """Highlight borders for given web element (using external JS file, preloaded)."""
    js = _HIGHLIGHT_ELEMENT_JS
    execute_javascript(js, element, draw_only, flash_border, color)


def get_by_attributes(
    elements: list[WebElement], locator: str, partial_match: bool
) -> dict[str, list[WebElement]]:
    """Return web element by its attribute value (using external JS file, preloaded)."""
    js = _GET_BY_ATTRIBUTES_JS
    return execute_javascript(js, elements, locator.replace("'", "\\'"), partial_match)


def get_all_elements(css: str) -> list[WebElement]:
    """Return all web elements for given css-locator.
    Parameters
    ----------
    css : selector
        For example: p,h1,h2,h3,input

    Returns
    -------
    list of web elements.
    """
    return execute_javascript("return document.querySelectorAll('{}')".format(css))


def get_childnodes(
    locator_element: WebElement, css: str, level: int = 3, traverse: bool = True
) -> list[WebElement]:
    """Find matching childs for given locator element (using external JS file, preloaded)."""
    js = _GET_CHILDNODES_JS
    return execute_javascript(js, locator_element, css, level, traverse)


def get_by_label(
    locator_text: str, css: str, level: int, partial_match: bool
) -> dict[str, list[WebElement]]:
    """Find element based on its label (using external JS file, preloaded)."""
    js = _GET_BY_LABEL_JS
    return execute_javascript(js, locator_text.replace("'", "\\'"), css, level, partial_match)


def get_parent_list(
    locator_element: Union[WebElement, str], css: str
) -> Union[WebElement, list[WebElement]]:
    """Get parent list for web element (using external JS file, preloaded)."""
    js = _GET_PARENT_LIST_JS
    return execute_javascript(js, locator_element, css)


def find_text_from_textnodes(text: str, **kwargs) -> list[WebElement]:
    """Find elements whose textContent matches to preferred text
       (using external JS file, preloaded)."""
    js = _FIND_TEXT_FROM_TEXTNODES_JS
    doc = "html"
    partial = kwargs.get("partial_match")
    return execute_javascript(js, text, doc, partial)


def get_clickable(locator: str) -> list[WebElement]:
    """Find clickable elements matching the locator (using external JS file, preloaded)."""
    js = _GET_CLICKABLE_JS
    return execute_javascript(js, locator)


def get_recursive_walk() -> str:
    """Return the recursiveWalk JS function as a string (using external JS file, preloaded)."""
    return _GET_RECURSIVE_WALK_JS


def get_text_elements_from_shadow_dom(locator: str, partial: bool) -> list[WebElement]:
    """Find elements in shadow DOM whose textContent matches to preferred text (using
       external JS file, preloaded)."""
    js = get_recursive_walk() + "\n" + _GET_TEXT_ELEMENTS_FROM_SHADOW_DOM_JS
    return execute_javascript(js, locator, partial)


def get_clickable_from_shadow_dom(locator: str, partial: bool) -> list[WebElement]:
    """Find clickable elements in shadow DOM matching the locator
       (using external JS file, preloaded)."""
    js = get_recursive_walk() + "\n" + _GET_CLICKABLE_FROM_SHADOW_DOM_JS
    return execute_javascript(js, locator, partial)


def get_all_frames_from_shadow_dom() -> list[WebElement]:
    """Find all iframe and frame elements in shadow DOM (using external JS file, preloaded)."""
    js = get_recursive_walk() + "\n" + _GET_ALL_FRAMES_FROM_SHADOW_DOM_JS
    return execute_javascript(js)


def get_all_input_elements_from_shadow_dom() -> list[WebElement]:
    """Find all input and textarea elements in shadow DOM (using external JS file, preloaded)."""
    js = get_recursive_walk() + "\n" + _GET_ALL_INPUT_ELEMENTS_FROM_SHADOW_DOM_JS
    return execute_javascript(js)


def get_all_dropdown_elements_from_shadow_dom() -> list[WebElement]:
    """Find all select elements in shadow DOM (using external JS file, preloaded)."""
    js = get_recursive_walk() + "\n" + _GET_ALL_DROPDOWN_ELEMENTS_FROM_SHADOW_DOM_JS
    return execute_javascript(js)


def get_item_elements_from_shadow_dom(tag: str) -> list[WebElement]:
    """Find item elements in shadow DOM matching supported tags or a given tag
       (using external JS file, preloaded)."""
    js = get_recursive_walk() + "\n" + _GET_ITEM_ELEMENTS_FROM_SHADOW_DOM_JS
    return execute_javascript(js, tag)


def create_toast_notification(message: str, level: str = "info", position: str = "center",
                              font_size: int = 18,
                              heading: str = "Test Automation Notification", timeout: int = 3):
    """Display toast notification in the browser via JavaScript (external file, preloaded)."""
    js = _TOAST_NOTIFICATION_JS
    js_call = (
        f"createToastNotification(\n"
        f"    {message!r},\n"
        f"    {level!r},\n"
        f"    {position!r},\n"
        f"    {font_size},\n"
        f"    {heading!r},\n"
        f"    {timeout}\n"
        f")"
    )
    full_js = js + "\n" + js_call
    return execute_javascript(full_js)
