# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

import pytest
from selenium.common.exceptions import (
    InvalidSelectorException,
    JavascriptException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from QWeb.internal import javascript
from QWeb.internal.exceptions import QWebStalingElementError


class _Driver:
    """Plain object so a missing attribute stays missing, unlike MagicMock."""

    def __init__(self):
        self.find_elements = MagicMock()
        self.find_element = MagicMock()
        self.execute_script = MagicMock()


def _unwrapped():
    return StaleElementReferenceException("stale element not found in the current frame")


def test_driver_result_is_returned_without_javascript():
    driver = _Driver()
    driver.find_elements.return_value = ["anchor"]

    assert javascript.find_elements_by_xpath(driver, "//a") == ["anchor"]

    driver.execute_script.assert_not_called()
    driver.find_elements.assert_called_once_with(By.XPATH, "//a")


def test_unwrapped_result_is_retried_in_the_page():
    driver = _Driver()
    driver.find_elements.side_effect = _unwrapped()
    driver.execute_script.return_value = ["anchor"]

    assert javascript.find_elements_by_xpath(driver, "//a") == ["anchor"]

    script, xpath = driver.execute_script.call_args[0]
    assert "doc.evaluate" in script
    assert "querySelectorAll" in script
    assert xpath == "//a"


def test_ordinary_stale_element_stays_on_the_driver():
    driver = _Driver()
    driver.find_elements.side_effect = StaleElementReferenceException(
        "element is not attached to the page document"
    )

    with pytest.raises(StaleElementReferenceException):
        javascript.find_elements_by_xpath(driver, "//a")

    driver.execute_script.assert_not_called()


def test_find_element_by_xpath_raises_when_nothing_matches():
    driver = _Driver()
    driver.find_elements.return_value = []

    with pytest.raises(NoSuchElementException):
        javascript.find_element_by_xpath(driver, "//missing")


def test_invalid_xpath_from_evaluate_is_an_invalid_selector():
    driver = _Driver()
    driver.find_elements.side_effect = _unwrapped()
    driver.execute_script.side_effect = JavascriptException(
        "The string '//' is not a valid XPath expression."
    )

    with pytest.raises(InvalidSelectorException):
        javascript.find_elements_by_xpath(driver, "//")


def test_predicate_pipe_is_an_invalid_selector():
    driver = _Driver()
    driver.find_elements.side_effect = _unwrapped()
    driver.execute_script.side_effect = JavascriptException(
        "Type conversion failed while evaluating the expression."
    )

    with pytest.raises(InvalidSelectorException):
        javascript.find_elements_by_xpath(driver, "//div[contains(@id,'a')|contains(@id,'b')]")


def test_union_is_searched_one_branch_at_a_time_when_the_whole_expression_fails():
    driver = _Driver()
    driver.find_elements.side_effect = _unwrapped()

    def run(_script, xpath):
        if "|" in xpath:
            raise InvalidSelectorException("type conversion failed while evaluating the expression")
        return [xpath]

    driver.execute_script.side_effect = run

    assert javascript.find_elements_by_xpath(driver, "//div | //span") == ["//div", "//span"]


def test_union_keeps_a_branch_the_driver_can_wrap():
    driver = _Driver()
    driver.find_elements.side_effect = _unwrapped()

    def run(_script, xpath):
        if "|" in xpath or "shadow" in xpath:
            raise StaleElementReferenceException("stale element not found in the current frame")
        return ["light"]

    driver.execute_script.side_effect = run

    found = javascript.find_elements_by_xpath(driver, "//a[@id='light'] | //a[@id='shadow']")

    assert found == ["light"]


def test_union_of_unwrapped_nodes_keeps_the_driver_message():
    driver = _Driver()
    driver.find_elements.side_effect = _unwrapped()
    driver.execute_script.side_effect = StaleElementReferenceException(
        "stale element not found in the current frame"
    )
    xpath = "(//a[@data-label='Sales'])[1] | (//a[@role='option']/*[.='Sales'])[1]"

    with pytest.raises(QWebStalingElementError) as caught:
        javascript.find_elements_by_xpath(driver, xpath)

    assert javascript.is_unwrapped_xpath_error(caught.value)


def test_other_javascript_errors_propagate():
    driver = _Driver()
    driver.find_elements.side_effect = _unwrapped()
    driver.execute_script.side_effect = JavascriptException("boom")

    with pytest.raises(JavascriptException):
        javascript.find_elements_by_xpath(driver, "//a")


def test_element_context_is_passed_to_evaluate(monkeypatch):
    driver = _Driver()

    class FakeElement:
        def __init__(self, parent):
            self.parent = parent

    def driver_cannot_wrap(*_args, **_kwargs):
        raise StaleElementReferenceException("stale element not found in the current frame")

    monkeypatch.setattr(javascript, "WebElement", FakeElement)
    monkeypatch.setattr(javascript, "_selenium_find_elements", driver_cannot_wrap)
    element = FakeElement(driver)
    driver.execute_script.return_value = []

    found = javascript.find_elements_by_xpath(element, ".//a")

    assert len(found) == 0
    assert driver.execute_script.call_args[0][1] is element
    assert driver.execute_script.call_args[0][2] == ".//a"


def test_driver_xpath_find_is_redirected():
    driver = _Driver()
    original_elements = driver.find_elements
    original_element = driver.find_element
    original_web_elements = WebElement.find_elements
    original_web_element = WebElement.find_element
    setattr(javascript, "_ELEMENT_XPATH_PATCHED", False)
    original_elements.return_value = ["anchor"]

    try:
        javascript.install_xpath_search(driver)
        assert driver.find_elements("xpath", "//a") == ["anchor"]
        driver.execute_script.assert_not_called()

        driver.find_elements("css selector", "a")
        assert original_elements.call_args_list == [
            (("xpath", "//a"),),
            (("css selector", "a"),),
        ]

        original_elements.return_value = []
        with pytest.raises(NoSuchElementException):
            driver.find_element("xpath", "//missing")
        original_element.assert_not_called()
    finally:
        WebElement.find_elements = original_web_elements
        WebElement.find_element = original_web_element
        setattr(javascript, "_ELEMENT_XPATH_PATCHED", False)
