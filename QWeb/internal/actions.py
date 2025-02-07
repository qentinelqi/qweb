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
"""Re-usable functions and private sub functions for common actions.

Timeouts and exceptions are handled in decorators.
Coding rules:
    1.) When implementing new features connect those to
        timeout_decorator_for_actions decorator for consistency.
    2.) Always use QWeb exceptions instead of Selenium or Python ones.
    3.) All exception and retry related logic should be handle
        in decorators for consistency and usability reasons.
"""

from __future__ import annotations

import fnmatch
import time
from typing import Any, Optional, Union

from robot.api import logger
from selenium.common.exceptions import (
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from QWeb.internal import browser, checkbox, decorators, javascript, util
from QWeb.internal import text as internal_text
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.exceptions import (
    QWebInvalidElementStateError,
    QWebTextNotFoundError,
    QWebTimeoutError,
    QWebUnexpectedConditionError,
    QWebValueError,
    QWebValueMismatchError,
)
from QWeb.internal.input_handler import INPUT_HANDLER as input_handler


@decorators.timeout_decorator_for_actions
def write(
    input_element: WebElement,
    input_text: str,
    timeout: int,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> None:
    click = util.par2bool(kwargs.get("click", CONFIG["ClickToFocus"]))
    if click:
        wd_click(input_element)
    if _ends_with_line_break(input_text):
        # input_text might be set to None from _remove_ending_line_break(input_text)
        input_text, key = _remove_ending_line_break(  # type: ignore[assignment]
            input_text
        )
        kwargs["key"] = key
    check = util.par2bool(kwargs.get("check", CONFIG["CheckInputValue"]))
    kwargs["shadow_dom"] = CONFIG["ShadowDOM"]
    if check is True:
        kwargs["check"] = True
        input_handler.write(input_element, input_text, **kwargs)
        time.sleep(1)
        compare_input_values(input_element, kwargs.get("expected", input_text), timeout=2, **kwargs)
        try:
            input_element.send_keys(kwargs.get("key", input_handler.line_break_key))
        except ElementNotInteractableException:
            # this can happen with firefox for shadow dom elements
            # log, but do not fail the test case as value was written correctly
            logger.debug("Could not send line break key to input")
    else:
        input_handler.write(input_element, input_text, **kwargs)
    logger.debug(f'Preferred text: "{input_text}"')


@decorators.timeout_decorator_for_actions
def compare_input_values(
    input_element: WebElement,
    expected_value: str,
    timeout: int,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> bool:
    try:
        real_value = input_value(input_element, timeout="0.5s", **kwargs)
        if expected_value == real_value:  # Full match
            return True
        real_value = util.get_substring(real_value, **kwargs)
        expected_value = str(util.get_substring(expected_value, **kwargs))
    except QWebValueError:
        real_value = ""
    logger.debug(f"Real value: {real_value}, expected value {expected_value}")
    if fnmatch.fnmatch(str(real_value).strip(), expected_value):
        return True
    raise QWebValueMismatchError(
        f"""Expected value "{expected_value}" didn\'t match to real value "{real_value}\""""
    )


@decorators.timeout_decorator_for_actions
def input_value(input_element: WebElement, timeout: int, **kwargs: Any) -> str:
    blind = util.par2bool(kwargs.get("blind", CONFIG["BlindReturn"]))
    shadow_dom = CONFIG["ShadowDOM"]

    if input_handler.is_editable_text_element(input_element) and not shadow_dom:
        value = input_element.get_attribute("innerText")
    else:
        value = input_element.get_attribute("value")
    if value:
        return value.strip()
    if blind:
        return ""
    raise QWebValueError(f"No Value found after {timeout} sec")


@decorators.timeout_decorator_for_actions
def scroll(web_element: WebElement, timeout: int) -> None:  # pylint: disable=unused-argument
    javascript.execute_javascript("arguments[0].scrollIntoView();", web_element)


def scroll_overlay_adjustment(overlay_offset: int = 0) -> None:  # pylint: disable=unused-argument
    previous_scroll = None
    driver = browser.get_current_browser()
    current_scroll = driver.execute_script("return window.pageYOffset;")

    # Keep checking until the scroll position stops changing
    # This was needed in firefox because the scroll position was not updated immediately
    while previous_scroll != current_scroll:
        previous_scroll = current_scroll
        time.sleep(0.2)  # Small delay to allow scrolling to stabilize
        current_scroll = driver.execute_script("return window.pageYOffset;")

    # scroll up by overlay offset
    # negative offset -> down, positive offset -> up
    scroll_amount = -overlay_offset if overlay_offset > 0 else abs(overlay_offset)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount})")


@decorators.timeout_decorator_for_actions
def execute_click_and_verify_condition(
    web_element: WebElement, text_appear: bool = True, **kwargs: Any
) -> bool:
    """Click and optionally verify condition after click.

    Accepted kwargs:
        text(str) = In case we want to verify that some text appears/disappears after click
        interval = How long we wait between the clicks
        timeout = How long we are trying if element is not enabled or some other error exists
        js = if js parameter exists, try javascript click instead of selenium
    """
    js = True if util.is_safari() else util.par2bool(kwargs.get("js", False))
    dbl_click = util.par2bool(kwargs.get("doubleclick", CONFIG["DoubleClick"]))
    if web_element.is_enabled():
        try:
            if dbl_click:
                if js:
                    js_double_click(web_element)
                else:
                    double_click(web_element)
            elif js:
                js_click(web_element)
            else:
                wd_click(web_element, **kwargs)
                logger.debug("element clicked")
        except WebDriverException as e:
            logger.info(f"Got {e} when tried to click.")
            if "text" not in kwargs:
                raise e
        if "text" in kwargs:
            logger.debug("button clicked. Verifying expected condition..")
            try:
                if text_appearance(
                    kwargs["text"], text_appear=text_appear, timeout=kwargs.get("interval")
                ):
                    return True
            except QWebTimeoutError as e:
                logger.debug("timeout err")
                raise QWebUnexpectedConditionError("Unexpected condition") from e
        return True
    raise QWebInvalidElementStateError("Element is not enabled")


def right_click(element: WebElement) -> None:
    driver = browser.get_current_browser()
    ac = ActionChains(driver)
    ac.context_click(element).perform()


def mouse_down(element: Optional[WebElement] = None) -> None:
    driver = browser.get_current_browser()
    ac = ActionChains(driver)
    if element:
        ac.click_and_hold(element)
    else:
        ac.click_and_hold()
    ac.perform()


def mouse_up(element: Optional[WebElement] = None) -> None:
    driver = browser.get_current_browser()
    ac = ActionChains(driver)
    if element:
        ac.release(element)
    else:
        ac.release()
    ac.perform()


def mouse_move(x: float, y: float) -> None:
    driver = browser.get_current_browser()
    ab = ActionBuilder(driver)
    ab.pointer_action.move_to_location(x, y)
    ab.perform()


def js_click(web_element: WebElement) -> None:
    javascript.execute_javascript("arguments[0].click()", web_element)
    logger.debug("Js click performed")


def js_double_click(web_element: WebElement) -> None:
    js = """var target = arguments[0];
            var clickEvent = document.createEvent('MouseEvents');
            clickEvent.initEvent ('dblclick', true, true);
            target.dispatchEvent(clickEvent);"""
    javascript.execute_javascript(js, web_element)
    logger.debug("Js double-click performed")


def double_click(web_element: WebElement) -> None:
    driver = browser.get_current_browser()
    ac = ActionChains(driver)
    ac.double_click(web_element)
    ac.perform()
    logger.debug("element double-clicked")


def wd_click(web_element: WebElement, **kwargs: Any) -> None:
    try:
        web_element.click()
    except WebDriverException as e:
        logger.debug(str(e))
        js_click_on_failure = util.par2bool(kwargs.get("js_click", True))
        if js_click_on_failure:
            js_click(web_element)


@decorators.timeout_decorator_for_actions
def checkbox_set(  # pylint: disable=unused-argument
    checkbox_element: WebElement, locator_element: WebElement, value: bool, **kwargs: Any
) -> None:
    if checkbox.is_checked(checkbox_element) != value:
        try:
            checkbox_element.click()
        except WebDriverException:
            if locator_element:
                locator_element.click()
            else:
                parent_elem = checkbox_element.find_element(By.XPATH, "..")
                if parent_elem.tag_name.lower() == "label":
                    parent_elem.click()
                if checkbox_element.is_selected() != value:
                    javascript.execute_javascript(
                        "arguments[0].checked={}".format("true" if value else "false"),
                        checkbox_element,
                    )


# pylint: disable=too-many-branches
@decorators.timeout_decorator_for_actions
def select_option(
    select: Select,  # pylint: disable=unused-argument
    option: str,
    unselect: bool = False,
    **kwargs: Any,
) -> bool:
    """Click and optionally verify condition after click.

    Parameters
    ----------
    select : object
        Instance of Select class
    option : str
        Text to select
    unselect : bool
        Select (False, default) or unselect (True) given option
    """
    option_list = []
    value_list = []
    if option.startswith("[[") and option.endswith("]]"):
        option = option.strip("[]")
        if option.isdigit():
            try:
                if unselect:
                    select.deselect_by_index(option)  # type: ignore
                else:
                    select.select_by_index(option)  # type: ignore
                return True
            except TypeError as te:
                raise QWebValueMismatchError("Index out of range") from te
    try:
        if unselect:
            select.deselect_by_visible_text(option)
        else:
            select.select_by_visible_text(option)
        return True
    except NoSuchElementException:
        try:
            if unselect:
                select.deselect_by_value(option)
            else:
                select.select_by_value(option)
            return True
        except NoSuchElementException:
            if select:
                for opt in select.options:
                    option_list.append(opt.text)
                    value_list.append(opt.get_attribute("value"))
        if option_list != value_list:
            raise QWebValueMismatchError(  # pylint: disable=W0707
                f'Option "{option}" is not in the options list.\n'
                f"The list contained these options: {option_list}.\n"
                f"The list contained these values: {value_list}."
            )
        raise QWebValueMismatchError(  # pylint: disable=W0707
            f'Option "{option}" is not in the options list.\n'
            f"The list contained these options: {option_list}.\n"
        )


@decorators.timeout_decorator_for_actions
def is_not_in_dropdown(select: Select, option: str, **kwargs: Any) -> bool:
    """ "Verifies that the selected option is not in the dropdown list"""
    option_list = get_select_options(select, **kwargs)
    if option in option_list:
        raise QWebValueError(f"Found the value {option} from the dropdown menu: {option_list}.")
    return True


@decorators.timeout_decorator_for_actions
def get_selected_value(
    select: Select,  # pylint: disable=unused-argument
    expected: Optional[str] = None,
    **kwargs: Any,
) -> Union[bool, str]:
    """Get or verify selected value.

    Parameters
    ----------
    select : object
        Instance of Select class
    expected : str
        Text to compare with selected value
    """
    sel_elems = select.all_selected_options
    selected = [ele.text for ele in sel_elems]

    txt_selected = ",".join(selected)

    if expected:
        if expected in selected:
            return True
        raise QWebValueMismatchError(
            f"""Expected value "{expected}" didn\'t match to real value "{txt_selected}"."""
        )
    return txt_selected


@decorators.timeout_decorator_for_actions
def get_select_options(
    select: Select,  # pylint: disable=unused-argument
    expected: Optional[str] = None,
    **kwargs: Any,
) -> Union[bool, list[str]]:
    options = select.options
    if expected:
        for option in options:
            logger.debug(option.text)
            if fnmatch.fnmatch(expected, option.text):
                return True
        raise QWebValueMismatchError(
            f'Expected value "{expected}" not found from selectable options'
        )
    # parse all options to a list and return it
    option_list = []
    for option in options:
        option_list.append(option.text)
    return option_list


@decorators.timeout_decorator_for_actions
def hover_to(web_element: WebElement, timeout: int = 0) -> None:  # pylint: disable=unused-argument
    driver = browser.get_current_browser()
    # firefox & safari specific fix
    needs_js_scroll = [
        x
        for x in [browser.firefox.NAMES, browser.safari.NAMES]
        if driver.capabilities["browserName"].lower() in x
    ]
    if needs_js_scroll:
        # use javascript to scroll
        logger.debug("Needs javascript to scoll")
        driver.execute_script("arguments[0].scrollIntoView(true);", web_element)
    try:
        hover = ActionChains(driver).move_to_element(web_element)
        hover.perform()
    except MoveTargetOutOfBoundsException:
        # chrome > 90, use javascript
        driver.execute_script("arguments[0].scrollIntoView(true);", web_element)


@decorators.timeout_decorator_for_actions
def text_appearance(text: str, **kwargs: Any) -> bool:
    """Sub for retry click.

    Works as keywords is_text and is_no_text. Returns True if
    text exists/not exists in given time. Raises QWebValueMismatchErr
    for decorator to handle if condition is not expected (False).
    """
    try:
        element = internal_text.get_element_by_locator_text(text, allow_non_existent=True, **kwargs)
    except QWebTimeoutError as te:
        if kwargs["text_appear"] is False:
            return True
        raise QWebValueMismatchError("return value should be true") from te
    try:
        if element and kwargs["text_appear"] is True:
            return True
        if not element and kwargs["text_appear"] is False:
            return True
    except QWebUnexpectedConditionError:
        logger.debug("StaleElement Err from text appearance")
    raise QWebValueMismatchError("return value should be true")


# pylint: disable=unused-argument
@decorators.timeout_decorator_for_actions
def get_element_text(
    web_element: WebElement, expected=None, timeout: int = 0, partial_match: bool = False
) -> Union[bool, str]:
    # if both text and innerText are missing, innerText would return None instead of ""
    # This needs to be handled here.
    real_text = (web_element.text or "").strip() or (
        web_element.get_attribute("innerText") or ""
    ).strip()

    if expected is not None:
        try:
            return _compare_texts(real_text, expected.strip(), partial_match)
        except QWebValueMismatchError as e:
            raise QWebValueError(f"Expected {expected}, found {real_text}") from e
    if real_text is not None:
        return real_text
    raise QWebValueMismatchError("Text not found")


def _compare_texts(text_to_compare: str, expected: str, partial_match: bool = True) -> bool:
    if text_to_compare == expected or (partial_match and expected in text_to_compare):
        return True
    raise QWebValueMismatchError(f"Expected {expected}, found {text_to_compare}")


def _ends_with_line_break(input_text: str) -> bool:
    line_break = ("\n", "\ue007", "\t", "\ue004")
    return input_text.endswith(line_break)


def _remove_ending_line_break(input_text: str) -> tuple[Optional[str], Optional[str]]:
    enter_key = ("\n", "\ue007")
    tab_key = ("\t", "\ue004")
    if input_text.endswith(enter_key):
        input_list = input_text.replace("\n", "\ue007").rsplit("\ue007", 1)
        return input_list[0], "\ue007"
    if input_text.endswith(tab_key):
        input_list = input_text.replace("\t", "\ue004").rsplit("\ue004", 1)
        return input_list[0], "\ue004"
    return None, None


def _contains_enter(input_text: str) -> bool:
    return bool("\n" in input_text or "\ue007" in input_text)


def _contains_tab(input_text: str) -> bool:
    return bool("\t" in input_text or "\ue004" in input_text)


def scroll_first_scrollable_parent_element(
    locator: str,
    anchor: str,
    text_to_find: str,
    scroll_length: Optional[Union[int, str]],
    slow_mode: bool,
    timeout: Union[int, float, str],
) -> None:
    visible = None
    js_get_parent_element = """
        function getScrollParent(node) {
          if (node == null) {
            return null;
          }

          if (node.scrollHeight > node.clientHeight) {
            return node;
          } else {
            return getScrollParent(node.parentNode);
          }
        }
        return getScrollParent(arguments[0]);
    """
    js_element_position = "return arguments[0].scrollTop;"
    js_element_scroll = f"arguments[0].scrollBy(0, {scroll_length or '1000'})"
    web_element = internal_text.get_element_by_locator_text(locator, anchor)
    scrollable_element = javascript.execute_javascript(js_get_parent_element, web_element)
    current_pos = javascript.execute_javascript(js_element_position, scrollable_element)
    old_pos = None
    start = time.time()
    if not slow_mode:
        while not visible and old_pos != current_pos and time.time() < float(timeout) + start:
            old_pos = javascript.execute_javascript(js_element_position, scrollable_element)
            javascript.execute_javascript(js_element_scroll, scrollable_element)
            time.sleep(0.5)
            current_pos = javascript.execute_javascript(js_element_position, scrollable_element)
            visible = internal_text.get_element_by_locator_text(
                text_to_find, allow_non_existent=True
            )
            logger.info(
                f"Old pos: {old_pos}\nNew pos: {current_pos}\nVisible: {visible}",
                also_console=True,
            )
    else:
        logger.info(
            f'\nSlow mode is on, execution will only stop if the text "{text_to_find}" '
            " is found or if the timeout is reached.",
            also_console=True,
        )
        while not visible and time.time() < float(timeout) + start:
            javascript.execute_javascript(js_element_scroll, scrollable_element)
            time.sleep(0.5)
            visible = internal_text.get_element_by_locator_text(
                text_to_find, allow_non_existent=True
            )
            logger.info(f"\nVisible: {visible}", also_console=True)
    if visible:
        return
    raise QWebTextNotFoundError(f"Text {text_to_find} not found.")


def scroll_dynamic_web_page(
    text_to_find: str,
    scroll_length: Optional[Union[int, str]],
    slow_mode: bool,
    timeout: Union[int, float, str],
) -> bool:
    visible = None
    js_browser_height = "return window.innerHeight"
    height = javascript.execute_javascript(js_browser_height)  # Length of one scroll
    js_current_pos = "return window.pageYOffset;"
    js_scroll = f"window.scrollBy(0,{scroll_length or height})"
    current_pos = javascript.execute_javascript(js_current_pos)
    old_pos = None
    start = time.time()
    if not slow_mode:
        while not visible and old_pos != current_pos and time.time() < float(timeout) + start:
            old_pos = javascript.execute_javascript(js_current_pos)
            javascript.execute_javascript(js_scroll)
            time.sleep(0.5)
            current_pos = javascript.execute_javascript(js_current_pos)
            visible = internal_text.get_element_by_locator_text(
                text_to_find, allow_non_existent=True
            )
            logger.info(
                f"\nOld pos: {old_pos}\nCurrent pos: {current_pos}\nVisible: {visible}",
                also_console=True,
            )
    else:
        logger.info(
            "\nSlow mode is on, execution will only stop if "
            f'the text "{text_to_find}" is found or if the timeout is reached.',
            also_console=True,
        )
        while not visible and time.time() < float(timeout) + start:
            javascript.execute_javascript(js_scroll)
            time.sleep(0.5)
            visible = internal_text.get_element_by_locator_text(
                text_to_find, allow_non_existent=True
            )
            logger.info(f"\nVisible: {visible}", also_console=True)

    if visible:
        return True
    raise QWebTextNotFoundError(
        f'Could not find text "{text_to_find}" after scrolling for {current_pos} pixels.'
    )
