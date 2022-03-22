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
import time
import fnmatch
from robot.api import logger
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, NoSuchElementException, \
    MoveTargetOutOfBoundsException, ElementNotInteractableException
from QWeb.internal.exceptions import QWebValueMismatchError, QWebValueError, \
    QWebUnexpectedConditionError, QWebInvalidElementStateError, QWebTimeoutError, \
    QWebTextNotFoundError
from QWeb.internal import text as internal_text, util
from QWeb.internal import javascript, decorators, checkbox, browser
from QWeb.internal.input_handler import INPUT_HANDLER as input_handler
from QWeb.internal.config_defaults import CONFIG


@decorators.timeout_decorator_for_actions
def write(input_element, input_text, timeout, **kwargs):  # pylint: disable=unused-argument
    click = util.par2bool(kwargs.get('click', CONFIG['ClickToFocus']))
    if click:
        wd_click(input_element)
    if _ends_with_line_break(input_text):
        input_text, key = _remove_ending_line_break(input_text)
        kwargs['key'] = key
    check = util.par2bool(kwargs.get('check', CONFIG['CheckInputValue']))
    kwargs['shadow_dom'] = CONFIG['ShadowDOM']
    if check is True:
        kwargs['check'] = True
        input_handler.write(input_element, input_text, **kwargs)
        time.sleep(1)
        compare_input_values(input_element, kwargs.get('expected', input_text), timeout=2, **kwargs)
        try:
            input_element.send_keys(kwargs.get('key', input_handler.line_break_key))
        except ElementNotInteractableException:
            # this can happen with firefox for shadow dom elements
            # log, but do not fail the test case as value was written correctly
            logger.debug("Could not send line break key to input")
    else:
        input_handler.write(input_element, input_text, **kwargs)
    logger.debug('Preferred text: "{}"'.format(input_text))


@decorators.timeout_decorator_for_actions
def compare_input_values(input_element, expected_value, timeout, **kwargs):  # pylint: disable=unused-argument
    try:
        real_value = util.get_substring(input_value(input_element, timeout="0.5s", **kwargs))
    except QWebValueError:
        real_value = ""
    logger.debug('Real value: {}, expected value {}'.format(real_value, expected_value))
    if fnmatch.fnmatch(real_value.strip(), expected_value):
        return True
    raise QWebValueMismatchError('Expected value "{}" didn\'t match to real value "{}"'
                                 .format(expected_value, real_value))


@decorators.timeout_decorator_for_actions
def input_value(input_element, timeout, **kwargs):
    blind = util.par2bool(kwargs.get('blind', CONFIG['BlindReturn']))
    shadow_dom = CONFIG['ShadowDOM']

    if input_handler.is_editable_text_element(input_element) and not shadow_dom:
        value = input_element.get_attribute('innerText')
    else:
        value = input_element.get_attribute('value')
    if value:
        return value.strip()
    if blind:
        return ''
    raise QWebValueError('No Value found after {} sec'.format(timeout))


@decorators.timeout_decorator_for_actions
def scroll(web_element, timeout):  # pylint: disable=unused-argument
    javascript.execute_javascript('arguments[0].scrollIntoView();', web_element)


@decorators.timeout_decorator_for_actions
def execute_click_and_verify_condition(web_element, text_appear=True, **kwargs):
    """Click and optionally verify condition after click.

    Accepted kwargs:
        text(str) = In case we want to verify that some text appears/disappears after click
        interval = How long we wait between the clicks
        timeout = How long we are trying if element is not enabled or some other error exists
        js = if js parameter exists, try javascript click instead of selenium
    """
    js = True if util.is_safari() else util.par2bool(kwargs.get('js', False))
    dbl_click = util.par2bool(kwargs.get('doubleclick', CONFIG["DoubleClick"]))
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
                logger.debug('element clicked')
        except WebDriverException as e:
            logger.info('Got {} when tried to click.'.format(e))
            if 'text' not in kwargs:
                raise e
        if 'text' in kwargs:
            logger.debug('button clicked. Verifying expected condition..')
            try:
                if text_appearance(kwargs['text'], text_appear=text_appear,
                                   timeout=kwargs.get('interval')):
                    return True
            except QWebTimeoutError as e:
                logger.debug('timeout err')
                raise QWebUnexpectedConditionError('Unexpected condition') from e
        return True
    raise QWebInvalidElementStateError('Element is not enabled')


def right_click(element):
    driver = browser.get_current_browser()
    ac = ActionChains(driver)
    ac.context_click(element).perform()


def js_click(web_element):
    javascript.execute_javascript('arguments[0].click()', web_element)
    logger.debug("Js click performed")


def js_double_click(web_element):
    js = """var target = arguments[0];
            var clickEvent = document.createEvent('MouseEvents');
            clickEvent.initEvent ('dblclick', true, true);
            target.dispatchEvent(clickEvent);"""
    javascript.execute_javascript(js, web_element)
    logger.debug("Js double-click performed")


def double_click(web_element):
    driver = browser.get_current_browser()
    ac = ActionChains(driver)
    ac.double_click(web_element)
    ac.perform()
    logger.debug('element double-clicked')


def wd_click(web_element, **kwargs):
    try:
        web_element.click()
    except WebDriverException as e:
        logger.debug(e)
        js_click_on_failure = util.par2bool(kwargs.get('js_click', True))
        if js_click_on_failure:
            js_click(web_element)


@decorators.timeout_decorator_for_actions
def checkbox_set(checkbox_element, locator_element, value,
                 **kwargs):  # pylint: disable=unused-argument
    if checkbox.is_checked(checkbox_element) != value:
        try:
            checkbox_element.click()
        except WebDriverException:
            if locator_element:
                locator_element.click()
            else:
                javascript.execute_javascript(
                    "arguments[0].checked={}".format("true" if value else "false"),
                    checkbox_element)


# pylint: disable=too-many-branches
@decorators.timeout_decorator_for_actions
def select_option(select, option, unselect=False, **kwargs):  # pylint: disable=unused-argument
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
    if option.startswith('[[') and option.endswith(']]'):
        option = option.strip('[]')
        if option.isdigit():
            try:
                if unselect:
                    select.deselect_by_index(option)
                else:
                    select.select_by_index(option)
                return True
            except TypeError as te:
                raise QWebValueMismatchError('Index out of range') from te
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
                    value_list.append(opt.get_attribute('value'))
        if option_list != value_list:
            raise QWebValueMismatchError(f'Option "{option}" is not in the options list.\n'  # pylint: disable=W0707
                                         f'The list contained these options: {option_list}.\n'
                                         f'The list contained these values: {value_list}.')
        raise QWebValueMismatchError(f'Option "{option}" is not in the options list.\n'  # pylint: disable=W0707
                                     'The list contained these options: {option_list}.\n')


@decorators.timeout_decorator_for_actions
def is_not_in_dropdown(select, option, **kwargs):
    """"Verifies that the selected option is not in the dropdown list"""
    option_list = get_select_options(select, **kwargs)
    if option in option_list:
        raise QWebValueError("Found the value {} from the dropdown menu: {}."
                             .format(option, option_list))
    return True


@decorators.timeout_decorator_for_actions
def get_selected_value(select, expected=None, **kwargs):  # pylint: disable=unused-argument
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
        raise QWebValueMismatchError('Expected value "{}" didn\'t match to real value "{}".'
                                     .format(expected, txt_selected))
    return txt_selected


@decorators.timeout_decorator_for_actions
def get_select_options(select, expected=None, **kwargs):  # pylint: disable=unused-argument
    options = select.options
    if expected:
        for option in options:
            logger.debug(option.text)
            if fnmatch.fnmatch(expected, option.text):
                return True
        raise QWebValueMismatchError(
            'Expected value "{}" not found from selectable options'.format(expected))
    # parse all options to a list and return it
    option_list = []
    for option in options:
        option_list.append(option.text)
    return option_list


@decorators.timeout_decorator_for_actions
def hover_to(web_element, timeout=0):  # pylint: disable=unused-argument
    driver = browser.get_current_browser()
    # firefox & safari specific fix
    needs_js_scroll = [x for x in [browser.firefox.NAMES, browser.safari.NAMES]
                       if driver.capabilities['browserName'].lower() in x]
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
def text_appearance(text, **kwargs):
    """ Sub for retry click.

    Works as keywords is_text and is_no_text. Returns True if
    text exists/not exists in given time. Raises QWebValueMismatchErr
    for decorator to handle if condition is not expected (False).
    """
    try:
        element = internal_text.get_element_by_locator_text(
            text, allow_non_existent=True, **kwargs)
    except QWebTimeoutError as te:
        if kwargs['text_appear'] is False:
            return True
        raise QWebValueMismatchError('return value should be true') from te
    try:
        if element and kwargs['text_appear'] is True:
            return True
        if not element and kwargs['text_appear'] is False:
            return True
    except QWebUnexpectedConditionError:
        logger.debug('StaleElement Err from text appearance')
    raise QWebValueMismatchError('return value should be true')


@decorators.timeout_decorator_for_actions
def get_element_text(web_element, expected=None, timeout=0):  # pylint: disable=unused-argument
    real_text = web_element.text.strip()
    if expected is not None:
        try:
            return _compare_texts(real_text, expected.strip(), timeout)
        except QWebValueMismatchError as e:
            raise QWebValueError('Expected {}, found {}'.format(expected, real_text)) from e
    if real_text is not None:
        return real_text
    raise QWebValueMismatchError('Text not found')


def _compare_texts(text_to_compare, expected, timeout):  # pylint: disable=unused-argument
    if fnmatch.fnmatch(text_to_compare, expected) is False:
        raise QWebValueMismatchError(
            'Expected {0}, found {1}'.format(expected, text_to_compare))
    return True


def _ends_with_line_break(input_text):
    line_break = ('\n', '\ue007', '\t', '\ue004')
    return input_text.endswith(line_break)


def _remove_ending_line_break(input_text):
    enter_key = ('\n', '\ue007')
    tab_key = ('\t', '\ue004')
    if input_text.endswith(enter_key):
        input_text = input_text.replace('\n', '\ue007').rsplit('\ue007', 1)
        return input_text[0], '\ue007'
    if input_text.endswith(tab_key):
        input_text = input_text.replace('\t', '\ue004').rsplit('\ue004', 1)
        return input_text[0], '\ue004'
    return None, None


def _contains_enter(input_text):
    return bool('\n' in input_text or '\ue007' in input_text)


def _contains_tab(input_text):
    return bool('\t' in input_text or '\ue004' in input_text)


def scroll_first_scrollable_parent_element(locator, anchor, text_to_find, scroll_length,
                                           slow_mode, timeout):
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
    js_element_scroll = "arguments[0].scrollBy(0, {})".format(scroll_length or '1000')
    web_element = internal_text.get_element_by_locator_text(locator, anchor)
    scrollable_element = javascript.execute_javascript(js_get_parent_element, web_element)
    current_pos = javascript.execute_javascript(js_element_position, scrollable_element)
    old_pos = None
    start = time.time()
    if not slow_mode:
        while not visible and old_pos != current_pos and time.time() < timeout + start:
            old_pos = javascript.execute_javascript(js_element_position, scrollable_element)
            javascript.execute_javascript(js_element_scroll, scrollable_element)
            time.sleep(.5)
            current_pos = javascript.execute_javascript(js_element_position, scrollable_element)
            visible = internal_text.get_element_by_locator_text(text_to_find,
                                                                allow_non_existent=True)
            logger.info('Old pos: {}\nNew pos: {}\nVisible: {}'
                        .format(old_pos, current_pos, visible), also_console=True)
    else:
        logger.info('\nSlow mode is on, execution will only stop if the text "{}" is found or if '
                    'the timeout is reached.'.format(text_to_find), also_console=True)
        while not visible and time.time() < timeout + start:
            javascript.execute_javascript(js_element_scroll, scrollable_element)
            time.sleep(.5)
            visible = internal_text.get_element_by_locator_text(text_to_find,
                                                                allow_non_existent=True)
            logger.info('\nVisible: {}'.format(visible), also_console=True)
    if visible:
        return
    raise QWebTextNotFoundError('Text {} not found.'.format(text_to_find))


def scroll_dynamic_web_page(text_to_find, scroll_length, slow_mode, timeout):
    visible = None
    js_browser_height = "return window.innerHeight"
    height = javascript.execute_javascript(js_browser_height)  # Length of one scroll
    js_current_pos = "return window.pageYOffset;"
    js_scroll = 'window.scrollBy(0,{})'.format(scroll_length or height)
    current_pos = javascript.execute_javascript(js_current_pos)
    old_pos = None
    start = time.time()
    if not slow_mode:
        while not visible and old_pos != current_pos and time.time() < timeout + start:
            old_pos = javascript.execute_javascript(js_current_pos)
            javascript.execute_javascript(js_scroll)
            time.sleep(.5)
            current_pos = javascript.execute_javascript(js_current_pos)
            visible = internal_text.get_element_by_locator_text(text_to_find,
                                                                allow_non_existent=True)
            logger.info('\nOld pos: {}\nCurrent pos: {}\nVisible: {}'
                        .format(old_pos, current_pos, visible), also_console=True)
    else:
        logger.info('\nSlow mode is on, execution will only stop if the text "{}" is found or if '
                    'the timeout is reached.'.format(text_to_find), also_console=True)
        while not visible and time.time() < timeout + start:
            javascript.execute_javascript(js_scroll)
            time.sleep(.5)
            visible = internal_text.get_element_by_locator_text(text_to_find,
                                                                allow_non_existent=True)
            logger.info('\nVisible: {}'.format(visible), also_console=True)

    if visible:
        return True
    raise QWebTextNotFoundError('Could not find text "{}" after scrolling for {} pixels.'
                                .format(text_to_find, current_pos))
