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
from typing import Any, Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    InvalidSelectorException,
    JavascriptException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from QWeb.internal import browser
from QWeb.internal.exceptions import QWebStalingElementError
from QWeb.internal.page_node import PageNode, elements_from_context


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
_FIND_BY_XPATH_JS = load_js('find_by_xpath.js')
_SHADOW_DOM_ACTION_JS = load_js('shadow_action.js')
_XPATH_ACTION_JS = load_js('xpath_action.js')


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
    # A node ChromeDriver cannot wrap is still the element the caller asked
    # for. Resolve it in the page instead of handing the handle to the driver.
    prepared: list[Any] = []
    resolve: list[str] = []
    for index, arg in enumerate(args):
        prepared.append(_script_argument(arg, "arguments[{0}]".format(index), resolve))
    if resolve:
        script = "\n".join(resolve) + "\n" + script
    return driver.execute_script(script, *prepared)


def _script_argument(value: Any, path: str, resolve: list[str]) -> Any:
    """Replace in-page nodes so a script argument list can be sent to the driver."""
    if isinstance(value, PageNode):
        resolve.append("{0} = (window.__qwebHeld || [])[{1}];".format(path, value.handle))
        return None
    if isinstance(value, list):
        return [
            _script_argument(item, "{0}[{1}]".format(path, index), resolve)
            for index, item in enumerate(value)
        ]
    if isinstance(value, tuple):
        return tuple(
            _script_argument(item, "{0}[{1}]".format(path, index), resolve)
            for index, item in enumerate(value)
        )
    return value


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
    needle = locator.replace("'", "\\'")
    # A script that returns an unwrappable node fails the whole call. Match those
    # here and let the driver compare only the nodes it can wrap.
    pages = [item for item in elements if isinstance(item, PageNode)]
    reals = [item for item in elements if not isinstance(item, PageNode)]
    found: dict[str, list[Any]] = {"full": [], "partial": []}
    if reals:
        matched = execute_javascript(js, reals, needle, partial_match)
        if isinstance(matched, dict):
            found["full"] = list(matched.get("full") or [])
            found["partial"] = list(matched.get("partial") or [])
    for node in pages:
        kind = _page_attribute_kind(node, needle, partial_match)
        if kind:
            found[kind].append(node)
    return found


def _page_attribute_kind(node: PageNode, locator: str, partial_match: bool) -> Optional[str]:
    """Same full/partial attribute rule as get_by_attributes.js."""
    for value in node.attributes().values():
        text = value.strip()
        if text == locator:
            return "full"
        if partial_match and locator in text:
            return "partial"
    return None


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


def shadow_dom_action(
    kind: str,
    text: str,
    index: int,
    partial: bool,
    tag: str = "",
    highlight: str = "",
    color: str = "blue",
    anchor: str = "",
    visibility: bool = True,
    offset: bool = True,
    viewport: bool = False,
) -> Union[bool, str]:
    """Find a shadow-DOM match and optionally click it without returning the node.

    ChromeDriver throws ``stale element not found in the current frame`` when a
    script returns a node whose parent chain ends in a synthetic shadow root.
    The action therefore stays in the page and reports only success or failure.
    ``debug`` means the match was highlighted and the click was left unperformed.
    """
    return execute_javascript(
        _SHADOW_DOM_ACTION_JS,
        kind,
        text,
        index,
        partial,
        tag,
        highlight,
        color,
        anchor,
        visibility,
        offset,
        viewport,
    )


def xpath_action(
    kind: str,
    xpath: str,
    index: int = 0,
    text: str = "",
    highlight: str = "",
    color: str = "blue",
    send_tab: bool = False,
    anchor: str = "",
    visibility: bool = True,
    offset: bool = True,
    viewport: bool = False,
) -> Union[bool, str]:
    """Click, type, or confirm an XPath match without returning the node."""
    return execute_javascript(
        _XPATH_ACTION_JS,
        kind,
        xpath,
        index,
        text,
        highlight,
        color,
        send_tab,
        anchor,
        visibility,
        offset,
        viewport,
    )


def get_text_elements_from_shadow_dom(locator: str, partial: bool) -> list[WebElement]:
    """Find elements in shadow DOM whose textContent matches to preferred text (using
       external JS file, preloaded)."""
    js = _GET_RECURSIVE_WALK_JS + "\n" + _GET_TEXT_ELEMENTS_FROM_SHADOW_DOM_JS
    return execute_javascript(js, locator, partial)


def get_clickable_from_shadow_dom(locator: str, partial: bool) -> list[WebElement]:
    """Find clickable elements in shadow DOM matching the locator
       (using external JS file, preloaded)."""
    js = _GET_RECURSIVE_WALK_JS + "\n" + _GET_CLICKABLE_FROM_SHADOW_DOM_JS
    return execute_javascript(js, locator, partial)


def get_all_frames_from_shadow_dom() -> list[WebElement]:
    """Find all iframe and frame elements in shadow DOM (using external JS file, preloaded)."""
    js = _GET_RECURSIVE_WALK_JS + "\n" + _GET_ALL_FRAMES_FROM_SHADOW_DOM_JS
    return execute_javascript(js)


def get_all_input_elements_from_shadow_dom(
    input_type: Optional[str] = None,
) -> list[WebElement]:
    """Find input and textarea elements in the document tree including shadow roots.

    Parameters
    ----------
    input_type : str, optional
        When set (e.g. ``"file"``), only ``INPUT`` elements with that ``type`` are returned.
        When omitted, all ``INPUT`` and ``TEXTAREA`` elements are returned.
    """
    js = _GET_RECURSIVE_WALK_JS + "\n" + _GET_ALL_INPUT_ELEMENTS_FROM_SHADOW_DOM_JS
    if input_type is not None:
        return execute_javascript(js, input_type)
    return execute_javascript(js)


def get_all_dropdown_elements_from_shadow_dom() -> list[WebElement]:
    """Find all select elements in shadow DOM (using external JS file, preloaded)."""
    js = _GET_RECURSIVE_WALK_JS + "\n" + _GET_ALL_DROPDOWN_ELEMENTS_FROM_SHADOW_DOM_JS
    return execute_javascript(js)


def get_item_elements_from_shadow_dom(
    tag: Optional[str], text: str = "", partial: bool = False
) -> list[Any]:
    """Find item elements in light DOM and shadow DOM.

    Shadow matches stay in the page. Returning them would make ChromeDriver
    reject the whole list, including the light-DOM matches.
    """
    js = _GET_RECURSIVE_WALK_JS + "\n" + _GET_ITEM_ELEMENTS_FROM_SHADOW_DOM_JS
    found = execute_javascript(js, tag, text, partial)
    return _matches_from_find_result(found)


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


def _xpath_driver(context: Union[WebDriver, WebElement]) -> WebDriver:
    if isinstance(context, WebElement):
        return context.parent
    return context


def _is_invalid_xpath_error(error: Exception) -> bool:
    message = str(error).lower()
    return (
        "not a valid xpath" in message
        or "not a legal expression" in message
        or "invalid xpath" in message
        or "invalid expression" in message
        or "invalid selector" in message
        or "type conversion failed" in message
    )


def is_unwrapped_xpath_error(error: BaseException) -> bool:
    """True only for the ChromeDriver error that drops a whole XPath result.

    The driver says ``stale element not found in the current frame`` when a
    returned node is not a native shadow node. The in-page search raises
    ``qweb-xpath-unwrapped`` for the same nodes. Other failures stay on the
    driver search, including a plain not-found and an ordinary stale element.
    """
    message = str(error).lower()
    return "qweb-xpath-unwrapped" in message or "stale element not found" in message


def _top_level_union_parts(xpath: str) -> list[str]:
    """Split an XPath union on ``|`` that is not inside quotes or brackets."""
    parts: list[str] = []
    current: list[str] = []
    paren = 0
    bracket = 0
    quote = ""
    for char in xpath:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "(":
            paren += 1
        elif char == ")":
            paren = max(0, paren - 1)
        elif char == "[":
            bracket += 1
        elif char == "]":
            bracket = max(0, bracket - 1)
        elif char == "|" and paren == 0 and bracket == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts or [xpath]


def _evaluate_xpath(
    driver: WebDriver, context: Union[WebDriver, WebElement], xpath: str
) -> list[WebElement]:
    """Run document.evaluate and return element nodes."""
    try:
        if isinstance(context, WebElement):
            found = driver.execute_script(_FIND_BY_XPATH_JS, context, xpath)
        else:
            found = driver.execute_script(_FIND_BY_XPATH_JS, xpath)
    except (JavascriptException, WebDriverException) as error:
        if is_unwrapped_xpath_error(error):
            raise QWebStalingElementError(str(error)) from error
        if _is_invalid_xpath_error(error):
            raise InvalidSelectorException(str(error)) from error
        raise
    return _matches_from_find_result(found)


def _matches_from_find_result(found: Any) -> list[Any]:
    """WebElements the driver accepted, plus handles for the nodes it cannot wrap."""
    if isinstance(found, dict):
        nodes = list(found.get("nodes") or [])
        result: list[Any] = []
        for item in found.get("order") or []:
            if isinstance(item, str) and item.startswith("m"):
                try:
                    result.append(PageNode(int(item[1:])))
                except ValueError:
                    continue
                continue
            try:
                result.append(nodes[int(item)])
            except (TypeError, ValueError, IndexError):
                continue
        return result
    if isinstance(found, (list, tuple)):
        return list(found)
    return []


def _unique_elements(elements: list[WebElement]) -> list[WebElement]:
    unique: list[WebElement] = []
    seen: set[int] = set()
    for element in elements:
        key = id(element)
        if key in seen:
            continue
        seen.add(key)
        unique.append(element)
    return unique


def _evaluate_union_parts(
    driver: WebDriver,
    context: Union[WebDriver, WebElement],
    parts: list[str],
    original: Exception,
) -> list[WebElement]:
    """Search each side of a union after the combined expression fails."""
    found: list[WebElement] = []
    unwrapped = False
    for part in parts:
        try:
            found.extend(_evaluate_xpath(driver, context, part))
        except InvalidSelectorException:
            raise original from None
        except (QWebStalingElementError, StaleElementReferenceException):
            unwrapped = True
    if found:
        return _unique_elements(found)
    if unwrapped:
        raise QWebStalingElementError(str(original)) from original
    raise original


def _find_by_javascript_xpath(
    driver: WebDriver, context: Union[WebDriver, WebElement], xpath: str
) -> list[WebElement]:
    try:
        return _evaluate_xpath(driver, context, xpath)
    except (
        QWebStalingElementError,
        StaleElementReferenceException,
        InvalidSelectorException,
    ) as error:
        parts = _top_level_union_parts(xpath)
        if len(parts) < 2:
            raise
        return _evaluate_union_parts(driver, context, parts, error)


def _is_xpath_strategy(by: Any) -> bool:
    return str(by).lower() == "xpath"


# Saved before install_xpath_search replaces the class methods.
_ORIGINAL_WEBELEMENT_FIND_ELEMENTS = WebElement.find_elements


def _selenium_find_elements(
    context: Union[WebDriver, WebElement], xpath: str
) -> list[WebElement]:
    """Call the original driver method, not a wrapper installed by ReturnBrowser."""
    if isinstance(context, WebElement):
        return list(_ORIGINAL_WEBELEMENT_FIND_ELEMENTS(context, By.XPATH, xpath))
    original = getattr(context, "_qweb_orig_find_elements", None)
    if original is not None:
        return list(original(By.XPATH, xpath))
    return list(context.find_elements(By.XPATH, xpath))


def find_elements_in_page(
    driver: WebDriver, xpath: str, context: Optional[WebElement] = None
) -> list[WebElement]:
    """Retry an XPath in the page and return the nodes ChromeDriver can wrap."""
    root = context if isinstance(context, WebElement) else driver
    return _find_by_javascript_xpath(driver, root, xpath)


def find_elements_by_xpath(
    context: Union[WebDriver, WebElement], xpath: str
) -> list[WebElement]:
    """Find elements by XPath.

    The browser driver searches first. When its result contains a node it cannot
    wrap, it raises ``stale element not found in the current frame`` and the
    whole result is discarded. Only that failure is retried in the page, where
    the matches are read back with querySelectorAll.
    """
    try:
        found = _selenium_find_elements(context, xpath)
    except (StaleElementReferenceException, QWebStalingElementError) as error:
        if not is_unwrapped_xpath_error(error):
            raise
        try:
            return _find_by_javascript_xpath(_xpath_driver(context), context, xpath)
        except (
            StaleElementReferenceException,
            QWebStalingElementError,
            JavascriptException,
        ) as retry_error:
            relative = xpath.lstrip().startswith(".")
            if (
                not relative
                or not isinstance(context, WebElement)
                or not is_unwrapped_xpath_error(retry_error)
            ):
                raise
            # Relative XPath from an element the driver already returned.
            # Read that same XPath back one element at a time.
            recovered = elements_from_context(context, xpath)
            if recovered:
                return recovered
            raise
    if found or not xpath.lstrip().startswith(("/", "(")):
        return found
    # Nothing in this document. A shadow-hosted frame is invisible to the
    # driver, but the XPath can still be read in that frame's document.
    try:
        return _find_by_javascript_xpath(_xpath_driver(context), context, xpath)
    except (StaleElementReferenceException, QWebStalingElementError, JavascriptException):
        return found


_ELEMENT_XPATH_PATCHED = False


def install_xpath_search(driver: WebDriver) -> None:
    """Route raw ``find_elements("xpath", ...)`` through the same XPath search.

    ``ReturnBrowser`` hands out the Selenium driver. Element-relative XPath is
    patched once. A result the driver cannot wrap is retried in the page.
    """
    global _ELEMENT_XPATH_PATCHED  # pylint: disable=global-statement
    if not getattr(driver, "_qweb_js_xpath", False):
        original_elements = driver.find_elements
        original_element = driver.find_element

        def find_elements(by: Any = "id", value: Optional[str] = None) -> list[WebElement]:
            if _is_xpath_strategy(by):
                return find_elements_by_xpath(driver, str(value))
            return original_elements(by, value)

        def find_element(by: Any = "id", value: Optional[str] = None) -> WebElement:
            if _is_xpath_strategy(by):
                return find_element_by_xpath(driver, str(value))
            return original_element(by, value)

        driver.find_elements = find_elements  # type: ignore[method-assign]
        driver.find_element = find_element  # type: ignore[method-assign]
        setattr(driver, "_qweb_orig_find_elements", original_elements)
        setattr(driver, "_qweb_js_xpath", True)

    if _ELEMENT_XPATH_PATCHED:
        return
    original_element_elements = WebElement.find_elements
    original_element_element = WebElement.find_element

    def element_find_elements(
        self: WebElement, by: Any = "id", value: Optional[str] = None
    ) -> list[WebElement]:
        if _is_xpath_strategy(by):
            return find_elements_by_xpath(self, str(value))
        return original_element_elements(self, by, value)

    def element_find_element(
        self: WebElement, by: Any = "id", value: Optional[str] = None
    ) -> WebElement:
        if _is_xpath_strategy(by):
            return find_element_by_xpath(self, str(value))
        return original_element_element(self, by, value)

    WebElement.find_elements = element_find_elements  # type: ignore[method-assign]
    WebElement.find_element = element_find_element  # type: ignore[method-assign]
    _ELEMENT_XPATH_PATCHED = True


def find_element_by_xpath(context: Union[WebDriver, WebElement], xpath: str) -> WebElement:
    """Return the first XPath match. Raises NoSuchElementException when there is none."""
    found = find_elements_by_xpath(context, xpath)
    if not found:
        raise NoSuchElementException(
            "no such element: Unable to locate element: "
            f"{{'method': 'xpath', 'selector': {xpath!r}}}"
        )
    return found[0]
