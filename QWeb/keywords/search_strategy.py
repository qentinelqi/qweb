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
"""Keywords for search strategies.

Search strategies define how elements are searched. With these settings
the search strategies can be tuned according to use case.
"""

from typing import Union
from QWeb.internal.search_strategy import SearchStrategies
from QWeb.keywords import config


def search_direction(direction: str) -> str:
    """*DEPRECATED!!* Use keyword `SetConfig  SearchDirection` instead.

    Set search direction for element search.

    Search direction is "up", "down", "left", "right" and "closest"

    Examples
    --------
    .. code-block:: robotframework

        SearchDirection    right
        SearchDirection    closest
    """
    return str(config.set_config("SearchDirection", direction))


def set_search_strategy(strategy_type: str, xpath: str) -> str:
    """*DEPRECATED!!* Use keyword `SetConfig` instead.

    Set search strategy for element search.

    Strategy type is either "all input elements", or "matching input element".

    "all input elements" is a plain xpath that is used to find all elements
    considered as input elements.

    "matching input element" is an xpath with mandatory placeholder "{}" for
    search string. Xpath expression is completed by xpath.format(locator)
    internally and therefore must include placeholder "{}". Used to find elements
    matching with a custom search string. Placeholder can be positional, such as {0}
    and repeated in that case.

    Returns previously used search strategy.


    Examples
    --------
    .. code-block:: robotframework

        Set search strategy    active area xpath    //input//textarea
        Set search strategy    all input elements    //input//textarea
        Set search strategy    matching input element    //*[@placeholder="{}"]
        Set search strategy    matching input element    containing input element
        ${previous}= Set search strategy    all input elements    //input
        Set search strategy    all input elements    ${previous}

    note: in the above case "containing input element" will use an xpath expression
    such that input elements that contain partial matches are used.

    Parameters
    ----------
    xpath : str
        xpath expression with or without "xpath = "

    Raises
    ------
    ValueError
        Wrong strategy type
    """
    if strategy_type == "all input elements":
        previous = config.set_config("AllInputElements", xpath)
    elif strategy_type == "matching input element":
        previous = config.set_config("MatchingInputElement", xpath)
    elif strategy_type == 'active area xpath':
        previous = config.set_config("ActiveAreaXpath", xpath)
    elif strategy_type == 'text':
        previous = config.set_config("TextMatch", xpath)
    elif strategy_type == 'containing text':
        previous = config.set_config("ContainingTextMatch", xpath)
    else:
        raise ValueError("Wrong strategy type")
    return previous


def default_timeout(timeout: Union[int, float, str]) -> Union[int, str]:
    """*DEPRECATED!!* Use keyword `SetConfig  DefaultTimeout` instead.

    Set default timeout for QWeb keywords.

    Timeout can be overridden by entering it manually

    Examples
    --------
    .. code-block:: robotframework

        DefaultTimeout    10s
        VerifyText        Foo
        VerifyText        Foo    60s
    """
    return config.set_config("DefaultTimeout", timeout)


def xhr_timeout(timeout: Union[int, float, str]) -> Union[int, str]:
    """*DEPRECATED!!* Use keyword `SetConfig  XHRTimeout` instead.

    Set default timeout for XHR (How log we wait page to be loaded).

    Timeout can be overridden by entering it manually

    Examples
    --------
    .. code-block:: robotframework

        XHRTimeout        60

    """
    return config.set_config("XHRTimeout", timeout)


def screenshot_type(capture_method: str) -> str:
    """*DEPRECATED!!* Use keyword `SetConfig  ScreenshotType` instead.

    Define how screenshot is taken. Default is normal screenshot.

    Html saves page as html frame in test log. All saves both image and html page.

    Examples
    --------
    .. code-block:: robotframework

        ScreenshotType        html
        ScreenshotType        screenshot
        ScreenshotType        all
    """
    return str(config.set_config("ScreenshotType", capture_method))


def css_selectors(state: str) -> str:
    """*DEPRECATED!!* Use keyword `SetConfig  CssSelectors` instead.

    Use CSS selectors for finding elements.

    CSS selectors is optional way to find elements that
    are difficult to catch by default selectors. Typically
    those elements are inputs, checkboxes and dropdowns
    without placeholder texts.

    With CSS selectors the detection is tried with:

    * Placeholder or tooltip

    * Label with 'for' attribute

    * DOM traversing to detect sibling element

    Examples
    --------
    .. code-block:: robotframework

        CssSelectors       on
        TypeText           MyLocator   Robot
        CssSelectors       off
    """
    return str(config.set_config("CssSelectors", state))


def check_input_value(state: Union[str, bool]) -> Union[str, bool]:
    r"""*DEPRECATED!!* Use keyword `SetConfig  CheckInputValue` instead.

    Check that real value matches to preferred value after TypeText.

    If value is not match we try to re type (three times before fail)
    This is optional feature. Default = false.
    Use with caution on elements where webdriver has tendency to lost focus
    and some part of the preferred text gone missing.


    Examples
    --------
    .. code-block:: robotframework

        CheckInputValue    True
        CheckInputValue    False

    Related keywords
    ----------------
    \`GetInputValue\`, \`VerifyInputElement\`, \`VerifyInputStatus\`,
    \`VerifyInputValue\`, \`VerifyInputValues\`
    """
    return bool(config.set_config("CheckInputValue", state))


def default_document(state: Union[str, bool]) -> Union[str, bool]:
    """*DEPRECATED!!* Use keyword `SetConfig  DefaultDocument` instead.

    Switches to default frame automatically.

    If some other frame is used by previous keyword
    we switch back to default after keyword is executed so
    that we are starting to find next locator from html document
    instead of previously used frame.
    Default = True
    Use False only when there is need to use and move
    between frames and page manually for some reason.


    Examples
    --------
    .. code-block:: robotframework

        DefaultDocument    True
        DefaultDocument    False
        DefaultDocument    On
        DefaultDocument    off

    """
    return config.set_config("DefaultDocument", state)


def case_insensitive(state: Union[str, bool]) -> Union[str, bool]:
    """*DEPRECATED!!* Use keyword `SetConfig  CaseInsensitive` instead.

    Set containing_text_match according to selected case sensitivity.

    Default = False
    Note: if containing_text_match has been overwritten manually
    this will return the default value.

    Examples
    --------
    .. code-block:: robotframework

        CaseInsensitive    True
        CaseInsensitive    False

    """
    case_state = config.set_config("CaseInsensitive", state)
    if case_state:
        config.set_config("ContainingTextMatch",
                          SearchStrategies.CONTAINING_TEXT_MATCH_CASE_INSENSITIVE)
    else:
        config.set_config("ContainingTextMatch",
                          SearchStrategies.CONTAINING_TEXT_MATCH_CASE_SENSITIVE)
    return case_state
