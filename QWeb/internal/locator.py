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
"""Parse locator strings given to *Element keywords.

Supported forms:

* ``//div``, ``(//div)[2]`` and ``xpath=//div``: XPath (default, unchanged behavior).
* ``css=div.card``: CSS selector.
* ``css=div.card:has-text("Hello")`` / ``css=div.card:text-is("Hello")``: CSS selector
  with a text filter at the end of the selector.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from QWeb.internal.exceptions import QWebInvalidSelectorError

XPATH = "xpath"
CSS = "css"
HAS_TEXT = "has-text"
TEXT_IS = "text-is"

_XPATH_PREFIX = "xpath="
_CSS_PREFIX = "css="
_FILTER_TOKENS = {":has-text(": HAS_TEXT, ":text-is(": TEXT_IS}
_COMBINATORS = (">", "+", "~")


@dataclass(frozen=True)
class TextFilter:
    """Text filter parsed from ``:has-text("...")`` or ``:text-is("...")``.

    ``text`` is normalized: trimmed, with whitespace runs collapsed to one space.
    """

    kind: str
    text: str


@dataclass(frozen=True)
class Locator:
    """Parsed locator.

    ``strategy`` is ``"xpath"`` or ``"css"``. ``value`` is the XPath expression or
    CSS selector without prefix and without text filter. ``raw`` is the original string,
    used in error messages.
    """

    strategy: str
    value: str
    raw: str
    text_filter: Optional[TextFilter] = None

    @property
    def is_css(self) -> bool:
        return self.strategy == CSS


def is_css_locator(locator: object) -> bool:
    """Return True if locator is a string starting with the ``css=`` prefix."""
    return isinstance(locator, str) and locator.lstrip().startswith(_CSS_PREFIX)


def normalize_text(text: str) -> str:
    """Trim text and collapse whitespace runs to a single space."""
    return " ".join(text.split())


def parse_locator(locator: str) -> Locator:
    """Parse locator string into strategy, value and optional text filter.

    XPath locators are returned as today: ``xpath=`` prefix is removed, anything
    else without the ``css=`` prefix is XPath as is.

    Raises
    ------
    QWebInvalidSelectorError
        If a ``css=`` locator has invalid syntax that can be detected without a
        browser (empty selector, misplaced or malformed text filter).
    """
    if is_css_locator(locator):
        selector = locator.strip()[len(_CSS_PREFIX) :].strip()
        return _parse_css(selector, locator)
    if locator.startswith(_XPATH_PREFIX):
        return Locator(XPATH, locator.split("=", 1)[1], locator)
    return Locator(XPATH, locator, locator)


def _invalid(raw: str, reason: str) -> QWebInvalidSelectorError:
    return QWebInvalidSelectorError(f"Invalid CSS selector in locator '{raw}': {reason}")


# pylint: disable=too-many-branches
def _parse_css(selector: str, raw: str) -> Locator:
    if not selector:
        raise _invalid(raw, "selector is empty")

    filters: list[tuple[int, str, int]] = []  # (start index, kind, nesting depth)
    has_top_level_comma = False
    depth = 0
    quote: Optional[str] = None
    i = 0
    while i < len(selector):
        char = selector[i]
        if char == "\\":
            i += 2  # CSS escape, skip next character
            continue
        if quote:
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        else:
            for token, kind in _FILTER_TOKENS.items():
                if selector.startswith(token, i):
                    filters.append((i, kind, depth))
                    break
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
            elif char == "," and depth == 0:
                has_top_level_comma = True
        i += 1

    if not filters:
        return Locator(CSS, selector, raw)
    if len(filters) > 1:
        raise _invalid(raw, "only one :has-text() or :text-is() filter is allowed")

    start, kind, filter_depth = filters[0]
    token = f":{kind}("
    if filter_depth != 0:
        raise _invalid(raw, f"{token}) is only allowed at the end of the selector")
    if has_top_level_comma:
        raise _invalid(raw, f"{token}) can't be combined with a selector list (,)")

    text, end = _read_filter_argument(selector, start + len(token), raw, token)
    if selector[end:].strip():
        raise _invalid(raw, f"{token}) is only allowed at the end of the selector")

    base = selector[:start]
    if not base.strip():
        raise _invalid(raw, f'{token}) needs a selector before it, e.g. css=*{token}"text")')
    if base != base.rstrip() or base.rstrip().endswith(_COMBINATORS):
        # "div :has-text(...)" means any descendant of div, like "div *"
        base = base + "*"

    normalized = normalize_text(text)
    if not normalized:
        raise _invalid(raw, f"{token}) text is empty")
    return Locator(CSS, base.strip(), raw, TextFilter(kind, normalized))


def _read_filter_argument(selector: str, pos: int, raw: str, token: str) -> tuple[str, int]:
    """Read quoted filter argument starting at pos.

    Returns the unescaped text and the index right after the closing parenthesis.
    """
    while pos < len(selector) and selector[pos].isspace():
        pos += 1
    if pos >= len(selector) or selector[pos] not in ("'", '"'):
        raise _invalid(raw, f"{token}) text must be in quotes")
    quote = selector[pos]
    pos += 1
    chars: list[str] = []
    while pos < len(selector):
        char = selector[pos]
        if char == "\\" and pos + 1 < len(selector):
            chars.append(selector[pos + 1])
            pos += 2
            continue
        if char == quote:
            break
        chars.append(char)
        pos += 1
    else:
        raise _invalid(raw, f"{token}) text has no closing quote")
    pos += 1  # closing quote
    while pos < len(selector) and selector[pos].isspace():
        pos += 1
    if pos >= len(selector) or selector[pos] != ")":
        raise _invalid(raw, f"{token}) is missing the closing parenthesis")
    return "".join(chars), pos + 1
