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

import pytest
from QWeb.internal.exceptions import (
    QWebInvalidSelectorError,
    QWebValueError,
    QWebElementNotFoundError,
)
from QWeb.internal.locator import (
    CSS_LOCATOR_KEYWORDS,
    parse_locator,
    is_css_locator,
    normalize_text,
    TextFilter,
    CSS,
    XPATH,
    HAS_TEXT,
    TEXT_IS,
)


@pytest.mark.parametrize(
    "locator, expected",
    [
        ("//div", "//div"),
        ("(//li[@class='item'])[4]", "(//li[@class='item'])[4]"),
        ("xpath=//div", "//div"),
        ('xpath=//input[@name="q"]', '//input[@name="q"]'),
        ("/html/body", "/html/body"),
        ("click_me", "click_me"),  # attribute value for tag= search, passed as is
        ("  //div", "  //div"),  # XPath is passed unchanged, as before
        ('//div[contains(., ":has-text(")]', '//div[contains(., ":has-text(")]'),
    ],
)
def test_xpath_locators_unchanged(locator, expected):
    parsed = parse_locator(locator)
    assert parsed.strategy == XPATH
    assert parsed.value == expected
    assert parsed.text_filter is None
    assert parsed.raw == locator
    assert not parsed.is_css


@pytest.mark.parametrize(
    "locator, expected",
    [
        ("css=button.primary", "button.primary"),
        ('css=input[name="q"]', 'input[name="q"]'),
        ("css=a[href='x=1&y=2']", "a[href='x=1&y=2']"),
        ("css=#user-menu > li:nth-child(2)", "#user-menu > li:nth-child(2)"),
        ("  css=  div.card  ", "div.card"),
        ("css=div, span", "div, span"),
        ('css=div:has(> p)', "div:has(> p)"),
        ('css=[title=":has-text(x)"]', '[title=":has-text(x)"]'),
        (r"css=#a\:has-text\(x\)", r"#a\:has-text\(x\)"),
    ],
)
def test_css_locators(locator, expected):
    parsed = parse_locator(locator)
    assert parsed.strategy == CSS
    assert parsed.is_css
    assert parsed.value == expected
    assert parsed.text_filter is None
    assert parsed.raw == locator


@pytest.mark.parametrize(
    "locator",
    ["CSS=div", "Css=div", "xpath=css=div", "//css=div", "cssdiv", "css div"],
)
def test_css_prefix_is_lowercase_and_at_start(locator):
    assert parse_locator(locator).strategy == XPATH
    assert not is_css_locator(locator)


@pytest.mark.parametrize(
    "locator, selector, kind, text",
    [
        ('css=div.card:has-text("Hello")', "div.card", HAS_TEXT, "Hello"),
        ("css=div.card:has-text('Hello')", "div.card", HAS_TEXT, "Hello"),
        ('css=div.card:text-is("Hello")', "div.card", TEXT_IS, "Hello"),
        ('css=div.card:has-text( "Hello" ) ', "div.card", HAS_TEXT, "Hello"),
        ('css=div.card:has-text("  Hello \n  world ")', "div.card", HAS_TEXT, "Hello world"),
        ("""css=p:has-text('Say "hi"')""", "p", HAS_TEXT, 'Say "hi"'),
        ('css=p:has-text("It\'s")', "p", HAS_TEXT, "It's"),
        (r'css=p:has-text("Say \"hi\"")', "p", HAS_TEXT, 'Say "hi"'),
        (r"css=p:has-text('It\'s')", "p", HAS_TEXT, "It's"),
        (r'css=p:has-text("back\\slash")', "p", HAS_TEXT, "back\\slash"),
        ('css=p:has-text("a) b")', "p", HAS_TEXT, "a) b"),
        ('css=p:has-text("x, y")', "p", HAS_TEXT, "x, y"),
        ('css=li.item:nth-child(2):has-text("Hi")', "li.item:nth-child(2)", HAS_TEXT, "Hi"),
        ('css=div.card :has-text("Hi")', "div.card *", HAS_TEXT, "Hi"),
        ('css=div.card > :has-text("Hi")', "div.card > *", HAS_TEXT, "Hi"),
        ('css=div.card>:has-text("Hi")', "div.card>*", HAS_TEXT, "Hi"),
        ('css=*:has-text("Hi")', "*", HAS_TEXT, "Hi"),
        ('css=div[data-x="a,b"]:has-text("Hi")', 'div[data-x="a,b"]', HAS_TEXT, "Hi"),
    ],
)
def test_text_filters(locator, selector, kind, text):
    parsed = parse_locator(locator)
    assert parsed.strategy == CSS
    assert parsed.value == selector
    assert parsed.text_filter == TextFilter(kind, text)
    assert parsed.raw == locator


@pytest.mark.parametrize(
    "locator, reason",
    [
        ("css=", "selector is empty"),
        ("css=   ", "selector is empty"),
        ('css=:has-text("Hi")', "needs a selector before it"),
        ('css=div:has-text("Hi") > button', "only allowed at the end"),
        ('css=div:has-text("Hi"):hover', "only allowed at the end"),
        ('css=div:not(:has-text("Hi"))', "only allowed at the end"),
        ('css=div:has-text("a"):text-is("b")', "only one"),
        ('css=div:has-text("a") span:has-text("b")', "only one"),
        ('css=div, span:has-text("Hi")', "selector list"),
        ("css=div:has-text(Hi)", "must be in quotes"),
        ('css=div:has-text("Hi)', "no closing quote"),
        ('css=div:has-text("Hi"', "missing the closing parenthesis"),
        ('css=div:has-text("Hi" x)', "missing the closing parenthesis"),
        ('css=div:has-text("")', "text is empty"),
        ('css=div:text-is("   ")', "text is empty"),
    ],
)
def test_invalid_css_locators(locator, reason):
    with pytest.raises(QWebInvalidSelectorError) as err:
        parse_locator(locator)
    assert reason in str(err.value)
    assert locator in str(err.value)


def test_invalid_selector_error_is_not_retried_type():
    # timeout_decorator retries QWebValueError and QWebElementNotFoundError,
    # so the invalid-selector error must not inherit from them
    assert not issubclass(QWebInvalidSelectorError, QWebValueError)
    assert not issubclass(QWebInvalidSelectorError, QWebElementNotFoundError)


@pytest.mark.parametrize(
    "value, expected",
    [(None, False), (123, False), ("css=div", True), ("  css=div", True), ("//div", False)],
)
def test_is_css_locator(value, expected):
    assert is_css_locator(value) is expected


def test_normalize_text():
    assert normalize_text("  a \n\t b  ") == "a b"
    assert normalize_text("") == ""


@pytest.mark.parametrize(
    "module, name",
    [
        ("QWeb.keywords.element", "click_element"),
        ("QWeb.keywords.text", "get_text"),
        ("QWeb.keywords.text", "verify_element_text"),
    ],
)
def test_css_locator_keywords(module, name):
    assert name in CSS_LOCATOR_KEYWORDS[module]


def test_tag_is_dropped_for_css_locator_in_text_keywords():
    # pylint: disable=import-outside-toplevel,protected-access
    from QWeb import QWeb
    from QWeb.keywords import text

    kwargs = {"tag": "div", "between": "a???b"}
    QWeb._drop_kwargs_ignored_with_css(text.get_text, ("css=#price",), kwargs)
    assert kwargs == {"between": "a???b"}
    kwargs = {"tag": "div"}
    QWeb._drop_kwargs_ignored_with_css(text.verify_element_text, ("css=#p", "x"), kwargs)
    assert not kwargs
    # text locators keep tag= (attribute search)
    kwargs = {"tag": "div"}
    QWeb._drop_kwargs_ignored_with_css(text.get_text, ("someattr",), kwargs)
    assert kwargs == {"tag": "div"}
