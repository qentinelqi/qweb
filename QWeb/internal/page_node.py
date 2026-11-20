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
"""Elements ChromeDriver refuses to wrap, addressed by an in-page handle."""
from __future__ import annotations

import importlib.resources
from typing import Any, Optional

from selenium.common.exceptions import (
    InvalidSelectorException,
    JavascriptException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from QWeb.internal import browser

_JS_FILE = importlib.resources.files("QWeb.internal.js").joinpath("page_node.js")
_PAGE_NODE_JS = _JS_FILE.read_text(encoding="utf-8")


class PageNode:
    """A DOM node kept in the page because ChromeDriver cannot wrap it."""

    def __init__(self, handle: int):
        self._handle = handle

    @property
    def handle(self) -> int:
        """Index of this node in the in-page list."""
        return self._handle

    def _call(self, command: str, extra: Any = None, flags: Any = None) -> dict:
        driver = browser.get_current_browser()
        try:
            result = driver.execute_script(_PAGE_NODE_JS, command, self._handle, extra, flags)
        except (JavascriptException, WebDriverException) as error:
            if _invalid_xpath(error):
                raise InvalidSelectorException(str(error)) from error
            raise
        if not isinstance(result, dict):
            raise StaleElementReferenceException(
                "stale element not found in the current frame"
            )
        if result.get("error") == "stale":
            raise StaleElementReferenceException("stale element not found in the current frame")
        if result.get("error") == "invalid":
            raise InvalidSelectorException(str(result.get("message") or "invalid selector"))
        return result

    @property
    def text(self) -> str:
        return str(self._call("text").get("value") or "")

    @property
    def tag_name(self) -> str:
        return str(self._call("tag").get("value") or "")

    def get_attribute(self, name: str) -> Optional[str]:
        value = self._call("attr", name).get("value")
        if value is None:
            return None
        return str(value)

    def attributes(self) -> dict[str, str]:
        """Every HTML attribute on this node."""
        value = self._call("attrs").get("value")
        if not isinstance(value, dict):
            return {}
        return {str(key): "" if item is None else str(item) for key, item in value.items()}

    def send_keys(self, *values: Any) -> None:
        """Type into this node. The driver cannot address it, so keys go to the focused element."""
        keys = [value for value in values if value is not None]
        if not keys:
            return
        self._call("focus")
        ActionChains(browser.get_current_browser()).send_keys(*keys).perform()

    @property
    def location(self) -> dict[str, float]:
        rect = self._call("rect").get("value") or {}
        return {"x": float(rect.get("x") or 0), "y": float(rect.get("y") or 0)}

    @property
    def size(self) -> dict[str, float]:
        rect = self._call("rect").get("value") or {}
        return {
            "width": float(rect.get("width") or 0),
            "height": float(rect.get("height") or 0),
        }

    def is_enabled(self) -> bool:
        """Same rule as ``element.is_enabled``: no disabled attribute."""
        return not bool(self.get_attribute("disabled"))

    def shown_flags(self) -> dict:
        """Visibility flags used by the normal element filter."""
        value = self._call("shown").get("value")
        return value if isinstance(value, dict) else {}

    def is_selected(self) -> bool:
        return bool(self._call("checked").get("value"))

    def _viewport_point(self) -> Optional[tuple[float, float]]:
        """Scroll the node into view and return its viewport center."""
        point = self._call("center").get("value") or {}
        try:
            x_pos = float(point.get("x") or 0)
            y_pos = float(point.get("y") or 0)
        except (TypeError, ValueError):
            return None
        if not x_pos and not y_pos:
            return None
        return x_pos, y_pos

    def _move_pointer(self, event_type: str, button: str = "none", buttons: int = 0) -> bool:
        point = self._viewport_point()
        if point is None:
            return False
        payload: dict[str, Any] = {"type": event_type, "x": point[0], "y": point[1]}
        if event_type != "mouseMoved":
            payload["button"] = button
            payload["buttons"] = buttons
            payload["clickCount"] = 1
        try:
            browser.get_current_browser().execute_cdp_cmd("Input.dispatchMouseEvent", payload)
        except WebDriverException:
            return False
        return True

    def hover(self) -> None:
        """Move the pointer onto this node. The driver cannot wrap it."""
        if not self._move_pointer("mouseMoved"):
            self._call("hover")

    def click(self) -> None:
        control = str(self.get_attribute("type") or "").lower()
        choice = self.tag_name.lower() == "input" and control in ("radio", "checkbox")
        before = self.is_selected() if choice else None
        moved = self._move_pointer("mouseMoved")
        pressed = moved and self._move_pointer("mousePressed", "left", 1)
        if not (pressed and self._move_pointer("mouseReleased", "left", 0)):
            self._call("click")
        if choice and before is False and not self.is_selected():
            self._call("activate-choice")

    def mark(self, color: str, mode: str) -> None:
        self._call("highlight", color, mode)

    def list_items(self, list_tag: str = "ul", direct: bool = False) -> list["PageNode"]:
        """Rows of the list that contains this node."""
        result = self._call("list-items", list_tag, direct)
        return [PageNode(int(handle)) for handle in result.get("handles") or []]

    def find_elements(self, by: str = By.XPATH, value: Optional[str] = None) -> list["PageNode"]:
        xpath = _relative_xpath(by, value)
        result = self._call("find", xpath)
        return [PageNode(int(handle)) for handle in result.get("handles") or []]

    def find_element(self, by: str = By.XPATH, value: Optional[str] = None) -> "PageNode":
        found = self.find_elements(by, value)
        if not found:
            raise NoSuchElementException(f"Unable to locate relative element: {value}")
        return found[0]

    def __repr__(self) -> str:
        return f"PageNode({self._handle})"


def list_items_from(start: Any, list_tag: str = "ul", direct: bool = False) -> list[PageNode]:
    """List rows when the driver cannot return the nodes closest() found."""
    if isinstance(start, PageNode):
        return start.list_items(list_tag, direct)
    driver = browser.get_current_browser()
    try:
        result = driver.execute_script(_PAGE_NODE_JS, "list-from", direct, start, list_tag)
    except (JavascriptException, WebDriverException) as error:
        if _invalid_xpath(error):
            raise InvalidSelectorException(str(error)) from error
        return []
    handles = result.get("handles") if isinstance(result, dict) else None
    return [PageNode(int(handle)) for handle in handles or []]


def export_xpath_matches(
    xpath: str, *, visibility: bool, offset: bool, viewport: bool
) -> list[Any]:
    """Mark each visible XPath match with an attribute the driver can look up."""
    driver = browser.get_current_browser()
    flags = {"visibility": visibility, "offset": offset, "viewport": viewport}
    try:
        tokens = driver.execute_script(_PAGE_NODE_JS, "export", xpath, None, flags)
    except (JavascriptException, WebDriverException) as error:
        if _invalid_xpath(error):
            raise InvalidSelectorException(str(error)) from error
        raise
    return list(tokens or [])


def elements_from_context(context: WebElement, xpath: str) -> list[WebElement]:
    """Resolve a relative XPath to WebElements when the driver drops the result."""
    driver = browser.get_current_browser()
    try:
        tokens = driver.execute_script(_PAGE_NODE_JS, "export-from", xpath, context, None)
    except (JavascriptException, WebDriverException) as error:
        if _invalid_xpath(error):
            raise InvalidSelectorException(str(error)) from error
        return []
    return web_elements_for_tokens(list(tokens or []))


def web_elements_for_tokens(tokens: list[Any]) -> list[WebElement]:
    """Read back nodes marked by an in-page export, one element at a time.

    Each entry is the match itself, then its parents. The first one ChromeDriver
    can wrap is the element returned for that match.
    """
    driver = browser.get_current_browser()
    elements: list[WebElement] = []
    for entry in tokens:
        chain = list(entry) if isinstance(entry, (list, tuple)) else [entry]
        chosen: Optional[WebElement] = None
        for token in chain:
            selector = '[data-qweb-ref="{}"]'.format(token)
            if chosen is None:
                try:
                    found = driver.find_elements(By.CSS_SELECTOR, selector)
                except (StaleElementReferenceException, WebDriverException):
                    found = []
                if found:
                    chosen = found[0]
            try:
                driver.execute_script(
                    "var node = document.querySelector(arguments[0]);"
                    "if (node) { node.removeAttribute('data-qweb-ref'); }",
                    selector,
                )
            except (JavascriptException, WebDriverException):
                continue
        if chosen is not None:
            elements.append(chosen)
    return elements


def hold_xpath_matches(
    xpath: str,
    *,
    visibility: bool,
    offset: bool,
    viewport: bool,
    context: Optional[WebElement] = None,
) -> list[PageNode]:
    """Evaluate an XPath and keep every match that cannot be returned.

    ``context`` is the same active-area element the driver search used.
    """
    driver = browser.get_current_browser()
    flags = {"visibility": visibility, "offset": offset, "viewport": viewport}
    try:
        handles = driver.execute_script(_PAGE_NODE_JS, "hold", xpath, context, flags)
    except (JavascriptException, WebDriverException) as error:
        if _invalid_xpath(error):
            raise InvalidSelectorException(str(error)) from error
        raise
    if not handles:
        return []
    return [PageNode(int(handle)) for handle in handles]


def _relative_xpath(by: str, value: Optional[str]) -> str:
    if value is None:
        value = str(by)
        by = By.XPATH
    if str(by).lower() not in {"xpath", str(By.XPATH).lower()}:
        raise InvalidSelectorException(f"Unsupported locator strategy '{by}'")
    return value


def _invalid_xpath(error: Exception) -> bool:
    message = str(error).lower()
    return (
        "qweb-invalid-xpath" in message
        or "not a valid xpath" in message
        or "invalid selector" in message
    )
