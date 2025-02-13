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
from typing import Optional, Union
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    InvalidSelectorException,
    JavascriptException,
    WebDriverException,
    NoSuchFrameException,
    NoSuchElementException,
)
from robot.api import logger
from QWeb.internal import element, javascript, frame, util, browser
from QWeb.internal.exceptions import (
    QWebElementNotFoundError,
    QWebValueError,
    QWebInstanceDoesNotExistError,
    QWebStalingElementError,
)
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.search_strategy import SearchStrategies


def get_element_by_locator_text(
    locator: str, anchor: str = "1", index: Union[int, str] = 1, **kwargs
) -> Optional[WebElement]:
    """Find element by it's visible text.

    Accepted kwargs:
        parent(tagName):Can be used when target element is some of the locators parent.
        child(tagName): Find clickable target from locator's child elements.
        allow_non_existent = True: Function returns immediately if element is not found
        css=False: Use this to bypass css search when finding elements by visible text
    """
    index = int(index) - 1
    try:
        web_element = get_text_using_anchor(locator, anchor, **kwargs)
    except (
        QWebElementNotFoundError,
        InvalidSelectorException,
        JavascriptException,
        WebDriverException,
    ):
        try:
            web_element = element.get_unique_element_by_xpath(locator, index=index)
        except (QWebElementNotFoundError, InvalidSelectorException, NoSuchFrameException) as e:
            no_raise = util.par2bool(kwargs.get("allow_non_existent", False))
            if no_raise:
                return None
            raise QWebElementNotFoundError(e) from e
    if web_element:
        if "parent" in kwargs and kwargs["parent"]:
            tag_name = kwargs["parent"]
            web_element = element.get_parent_element(web_element, tag_name)
        elif "child" in kwargs and kwargs["child"]:
            tag_name = kwargs["child"]
            web_element = element.get_element_from_childnodes(
                web_element, tag_name, dom_traversing=False
            )[int(index)]
        if CONFIG["SearchMode"]:
            element.draw_borders(web_element)
        return web_element
    raise QWebElementNotFoundError("Element not found")


@frame.all_frames
def find_text(text: str) -> bool:
    try:
        if javascript.execute_javascript(
            "return window.find('{}')".format(text.replace("'", "\\'"))
        ):
            return True
    except WebDriverException as e:
        logger.debug("Got webdriver exception from find text func: {}".format(e))
    raise QWebElementNotFoundError("Text not found")


def get_text_elements(text: str, **kwargs) -> Optional[list[WebElement]]:
    web_elements: Optional[list[WebElement]] = None
    xpath_elements: Optional[list[WebElement]] = None
    slot_elements: Optional[list[WebElement]] = None
    try:
        web_elements = _get_exact_text_element(text, **kwargs)
    except NoSuchFrameException:
        logger.debug("Got no such frame from get exact text")
    partial = util.par2bool(kwargs.get("partial_match", CONFIG["PartialMatch"]))
    if partial:
        try:
            web_elements = _get_contains_text_element(text, **kwargs)
        except NoSuchFrameException:
            logger.debug("Got no such frame from contains text")
    # find text directly from slots with supported parent elements
    slot_elements = get_slot_elements(text, partial)
    if slot_elements:
        xpath_elements = element.get_visible_elements_from_elements(slot_elements, **kwargs) or None
    if xpath_elements:
        if web_elements is None:
            web_elements = []  # Initialize web_elements to an empty list if it's None
        web_elements = web_elements + xpath_elements
    shadow_dom = CONFIG["ShadowDOM"]
    if shadow_dom:
        shadow_elements = get_texts_including_shadow_dom(text, partial, **kwargs)
        # remove possible stale elements
        web_elements = util.remove_stale_elements(web_elements)  # type: ignore
        # remove duplicates
        web_elements = util.remove_duplicates_from_list(shadow_elements, web_elements)  # type: ignore # pylint: disable=C0301

    return web_elements


def get_unique_text_element(text: str, **kwargs) -> WebElement:
    """Get element with text that is unique.

    First tries to find exact match and if not found then search as a
    substring.

    Parameters
    ----------
    text : str
        Text to be searched.

    Returns
    -------
    WebElement
        Webelement that has the text.

    Raises
    ------
    NoSuchElementException
        There are not elements with the given text.
    ValueError
        Found many elements with the given text.
    """
    web_elements = get_text_elements(text, **kwargs)
    if not web_elements:
        raise QWebValueError('Text "{}" did not match any elements'.format(text))
    if len(web_elements) == 1:
        return web_elements[0]  # pylint: disable=unsubscriptable-object
    raise QWebValueError(
        'Text "{}" matched {} elements. Needs to be unique'.format(text, len(web_elements))
    )


@frame.all_frames
def check_all_nodes(text: str, **kwargs) -> Optional[list[WebElement]]:
    try:
        return element.get_visible_elements_from_elements(
            javascript.find_text_from_textnodes(text, **kwargs)
        )
    except (
        WebDriverException,
        NoSuchFrameException,
        JavascriptException,
        QWebStalingElementError,
    ) as e:
        logger.info("Got {} from check all nodes".format(e))
        return None


def get_all_text_elements(text: str, **kwargs) -> list[WebElement]:
    """Get all webelements found by text"""
    web_elements: list[WebElement] = []
    shadow_dom = CONFIG["ShadowDOM"]
    all_text_nodes = util.par2bool(kwargs.get("all_text_nodes", CONFIG["AllTextNodes"]))
    kwargs["partial_match"] = kwargs.get("partial_match", CONFIG["PartialMatch"])
    if all_text_nodes:
        web_elements = check_all_nodes(text, **kwargs)
        if web_elements:
            return web_elements

    if "css" not in kwargs:
        try:
            web_elements = get_clickable_elements(text, shadow_dom=shadow_dom, **kwargs)
        except (
            JavascriptException,
            WebDriverException,
            NoSuchFrameException,
            QWebStalingElementError,
        ) as e:
            logger.debug("got {}. Syntax might be invalid".format(e))
    if not web_elements:
        # shadow dom search for all texts is done inside get_text_elements
        web_elements = get_text_elements(text, **kwargs)  # type: ignore[assignment]
    if not web_elements:
        raise QWebElementNotFoundError('Webpage did not contain text "{}"'.format(text))
    return web_elements


def get_text_using_anchor(text: str, anchor: str, **kwargs) -> WebElement:
    """Get WebElement that contains text using anchor if necessary.

    First locates the elements that has the exact text. If no elements were
    found then searching as a substring using XPath's contains function. If
    we come up empty then NoSuchElementException is raised.

    If text corresponded to multiple elements then anchor is taken in to
    play.

    Parameters
    ----------
    text : str
        Text on web page that is wanted to locate.
    anchor : str
        Unique text on web page which is close to the first argument.
    Accepted kwargs:
        css=False/off: Use this to bypass css search when finding elements
        by visible text

    Returns
    -------
    WebElement
    """
    web_elements = get_all_text_elements(text, **kwargs)

    # filter elements by modal (dialog etc) if needed
    web_elements = filter_by_modal_ancestor(web_elements)
    if not web_elements:
        raise QWebElementNotFoundError('Webpage did not contain text "{}"'.format(text))

    # return directly if 1 match and direction does not need to be checked
    if len(web_elements) == 1 and not CONFIG.enforce_direction():
        return web_elements[0]
    # Found many elements, use anchors to determine correct element
    correct_element = get_element_using_anchor(web_elements, anchor, **kwargs)
    return correct_element


def _get_exact_text_element(text: str, **kwargs) -> Optional[list[WebElement]]:
    xpath = CONFIG["TextMatch"].replace('"{0}"', util.escape_xpath_quotes(text))
    return element.get_webelements_in_active_area(xpath, **kwargs)


def _get_contains_text_element(text: str, **kwargs) -> list[WebElement]:
    xpath = CONFIG["ContainingTextMatch"].replace('"{0}"', util.escape_xpath_quotes(text))
    return element.get_webelements_in_active_area(xpath, **kwargs)


def filter_by_modal_ancestor(elements: list[WebElement]) -> list[WebElement]:
    xpath = CONFIG["IsModalXpath"]
    if xpath.startswith("xpath="):
        xpath = xpath.split("=", 1)[1]
    if xpath.startswith("//"):
        xpath = xpath[2:]

    modal_xpath = CONFIG["IsModalXpath"]
    driver = browser.get_current_browser()
    # no filtering if modal setting is the default one
    if modal_xpath == SearchStrategies.IS_MODAL_XPATH:
        return elements

    # filter elements by modal (dialog etc)
    logger.debug("IsModalXpath filtering on, filtering...")
    modal_exists = driver.find_elements(By.XPATH, modal_xpath)
    # no filtering if modal element doesn't exist
    if not modal_exists:
        return elements

    logger.debug(f"length before filtering: {len(elements)}")
    elems_in_modal = []

    for elem in elements:
        try:
            elem.find_element(By.XPATH, f"./../ancestor::{xpath}")
            elems_in_modal.append(elem)
        except NoSuchElementException:
            logger.debug("Filtering out element, modal open but not under modal")
            continue

    logger.debug(f"length after filtering: {len(elems_in_modal)}")
    return elems_in_modal


def get_element_using_anchor(
    elements: list[WebElement], anchor: Optional[Union[str, int]], **kwargs
) -> WebElement:
    """Determine correct element from list of elements using anchor.

    Parameters
    ----------
    elements : :obj:`list` of :obj:`WebElement`
    anchor

    Returns
    -------
    WebElement
    """
    if anchor is None:
        # Element was not unique and anchor was not used.
        raise QWebValueError(
            "Found {} elements. Use anchor to determine which is wanted".format(len(elements))
        )
    # Select by index unless anchor type is text
    if str(anchor).isdigit() and kwargs.get("anchor_type", "auto").lower() != "text":
        anchor_int = int(anchor) - 1
        if anchor_int < len(elements):
            return elements[anchor_int]
        raise QWebInstanceDoesNotExistError(
            "Found {} elements. Given anchor was {}".format(len(elements), anchor_int + 1)
        )
    if isinstance(anchor, str):  # Get closest element to anchor
        kwargs["stay_in_current_frame"] = True
        anchor_element: Optional[WebElement]
        if CONFIG["MultipleAnchors"]:
            anchor_elements: list[WebElement] = []
            logger.debug("Multiple anchors enabled, trying to find first exact match")
            try:
                anchor_elements = _get_exact_text_element(  # type: ignore[assignment]
                    anchor, **kwargs
                )
            except NoSuchFrameException:
                logger.debug("Got no such frame from get exact text")
            if len(anchor_elements) > 0:
                # Using first exact match as anchor

                # We need to return the element that has the text, not parent
                anchor_element = _get_anchor_with_inner_text(
                    anchor_elements, anchor, exact_match=True
                )
                anchor_element = anchor_element or anchor_elements[0]
            else:
                # No exact matches found, trying to find partial
                anchor_elements = get_text_elements(  # type: ignore[assignment]
                    anchor, **kwargs
                )
                if len(anchor_elements) > 0:
                    logger.debug("No exact match found, using first partial match")
                    # We need to return the element that includes the text, not parent
                    anchor_element = _get_anchor_with_inner_text(
                        anchor_elements, anchor, exact_match=False
                    )

                    anchor_element = anchor_element or anchor_elements[0]
                else:
                    raise QWebElementNotFoundError(f"Could not find elements for anchor: {anchor}")
        else:
            anchor_element = get_unique_text_element(anchor, **kwargs)
        return element.get_closest_element(anchor_element, elements)
    raise TypeError("Unknown argument type {}".format(type(anchor)))


def get_item_using_anchor(text: str, anchor: str, **kwargs) -> Optional[WebElement]:
    xpath = (
        '//*[@title="{0}" or @alt="{0}" or @data-tooltip="{0}" or '
        '@tooltip="{0}" or @aria-label="{0}" or @data-icon="{0}"]'.format(text)
    )
    if CONFIG["CssSelectors"]:
        web_elements = _get_item_by_css(text, **kwargs) or _get_item_by_xpath(text, **kwargs)
    else:
        web_elements = element.get_webelements(xpath, **kwargs)
    # extend search to Shadow DOM
    shadow_dom = CONFIG["ShadowDOM"]
    if shadow_dom:
        tag = kwargs.get("tag", None)
        elements = get_items_including_shadow_dom(text, tag)

        if web_elements:
            for el in elements:
                if el not in list(web_elements):
                    web_elements.append(el)
        else:
            web_elements = elements
    if web_elements:
        correct = _get_correct_element(web_elements, str(anchor), **kwargs)
        if CONFIG["SearchMode"]:
            element.draw_borders(correct)
        return correct
    no_raise = util.par2bool(kwargs.get("allow_non_existent", False))
    if no_raise:
        return None
    raise QWebElementNotFoundError("Cannot find item for locator {}".format(text))


def _get_correct_element(web_elements: list[WebElement], anchor: str, **kwargs) -> WebElement:
    if len(web_elements) == 1:
        return web_elements[0]
    correct_element = get_element_using_anchor(web_elements, anchor, **kwargs)
    return correct_element


def _get_item_by_css(text: str, **kwargs) -> Optional[list[WebElement]]:
    """
    Allows partial match. Anchor has to be number.
    :param text: str
        Attribute value of the element
    :return:
        webelement that containing attribute with given value
    """
    if "partial_match" not in kwargs:
        kwargs["partial_match"] = True
    css = (
        "a, span, img, li, h1, h2, h3, h4, h5, h6, div, svg, p, button, input"
        ':not([type="text"]):not([type="password"]):not([type="email"])'
    )
    # get_elements_by_attributes already handles going through frames
    kwargs["continue_search"] = False
    full, partial = element.get_elements_by_attributes(css, text, **kwargs)
    web_elements = element.get_visible_elements_from_elements(full + partial, **kwargs)
    if web_elements:
        return web_elements
    return None


def _get_item_by_xpath(text: str, **kwargs) -> Optional[list[WebElement]]:
    """
    Backup search for finding items by attribute via xpath.
    Needed in cases where there a slots that can't be pierced through
    with javascript.

    Allows partial match. Anchor has to be number.
    :param text: str
        Attribute value of the element
    :return:
        webelement that containing attribute with given value
    """
    if "partial_match" not in kwargs:
        kwargs["partial_match"] = True
    xpath = (
        "//a | //span | //img | //li | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //div | //svg | "
        "//p | //button | //input[not(@type='text') and not(@type='password') and "
        "not(@type='email')]"
    )
    # get_elements_by_attributes already handles going through frames
    kwargs["continue_search"] = False
    full, partial = element.get_elements_by_attributes(xpath, text, **kwargs)
    web_elements = element.get_visible_elements_from_elements(full + partial, **kwargs)
    if web_elements:
        return web_elements
    return None


def _get_anchor_with_inner_text(
    anchor_elements: list[WebElement], anchor: str, exact_match: bool = True
) -> Optional[WebElement]:
    """
    Finds the appropriate anchor element containing the given text in innertext based on
    whether we are searching for an exact match or partial match.

    Parameters:
    - anchor_elements: List[WebElement], a list of WebElement objects to search through.
    - anchor: str, the text to match against the element's innerText.
    - exact_match: bool, specifies whether to look for an exact match or partial match.

    Returns:
    - Optional[WebElement]
    """

    for el in anchor_elements:
        inner_text = el.get_attribute("innerText") or ""
        if (exact_match and anchor == inner_text) or (not exact_match and anchor in inner_text):
            return el
    return None


def get_slot_elements(locator: str,
                      partial_match: bool = False) -> Optional[list[WebElement]]:
    """
    Retrieve text from supported slot elements based on a locator string. Slots are by default
    not visible (no offset), but some systems like Salesforce put texts directly in slots.
    This function allows to retrieve these elements, if text is directly in a slot which is
    a child element to a visible <a> element. The returned element is the parent element.

    Args:
        locator (str): The string to locate elements by.
        partial_match (bool): Whether to use partial matching.

    Returns:
        Optional[List[WebElement]]: List of clickable WebElement objects, or None if none found.
    """
    # slots with matching direct text with parent <a> are currently supported
    if partial_match:
        xpath = (
            '//a[descendant::slot[contains('
            'normalize-space(translate(., "\u00a0", " ")), '
            f'"{locator}")]]'
        )
    else:
        xpath = f'//a[descendant::slot[normalize-space(translate(., "\u00a0", " "))="{locator}"]]'

    # handle quotes
    xpath = xpath.replace(f'"{locator}"', util.escape_xpath_quotes(locator))

    # Find slots with text and get/return their parent link
    driver = browser.get_current_browser()

    # if any other weird characters or combinations that might break xpath,
    # return None instead of throwing an exception
    try:
        xpath_elements = driver.find_elements(By.XPATH, xpath)
    except InvalidSelectorException:
        return None
    return xpath_elements


@frame.all_frames
def get_clickable_elements(
    locator: str, shadow_dom: bool = False, **kwargs
) -> Optional[list[WebElement]]:
    """
    Retrieve clickable elements based on a locator string.

    Args:
        locator (str): The string to locate elements by.
        shadow_dom (bool): Whether to search within shadow DOM.
        partial_match (bool): Whether to use partial matching.
        **kwargs: Additional keyword arguments.

    Returns:
        Optional[List[WebElement]]: List of clickable WebElement objects, or None if none found.
    """
    partial = util.par2bool(kwargs.get("partial_match", False))

    # Find text directly in slots with supported parent elements
    xpath_elements = get_slot_elements(locator, partial)

    # Find normal elements via javascript
    if shadow_dom:
        js_elements = javascript.get_clickable_from_shadow_dom(locator, partial)
    else:
        js_elements = javascript.get_clickable(locator)

    if js_elements:
        logger.debug(f"Found elements by js: {js_elements}")

    # merge found elements and check visibility
    if not xpath_elements:
        xpath_elements = []
    else:
        logger.debug(f"Found elements by xpath: {xpath_elements}")
    if js_elements:
        util.remove_duplicates_from_list(js_elements, xpath_elements)
        # util.remove_stale_elements(xpath_elements)
    if xpath_elements:
        return element.get_visible_elements_from_elements(xpath_elements, **kwargs)
    return None


@frame.all_frames
def get_texts_including_shadow_dom(locator: str, partial: bool, **kwargs) -> list[WebElement]:
    web_elements = element.get_visible_elements_from_elements(
        javascript.get_text_elements_from_shadow_dom(locator, partial), **kwargs
    )
    if web_elements:
        logger.debug("Found elements from shadow dom: {}".format(web_elements))
    return web_elements


@frame.all_frames
def get_items_including_shadow_dom(text: str, tag: str, **kwargs) -> list[WebElement]:
    web_elements = element.get_visible_elements_from_elements(
        javascript.get_item_elements_from_shadow_dom(tag), **kwargs
    )

    matches = javascript.get_by_attributes(web_elements, text, False)
    full, partial = matches.get("full", []), matches.get("partial", [])
    shadow_elements = full + partial
    if shadow_elements:
        logger.debug(f"Found {len(shadow_elements)} items when extending search to shadow dom")
    return shadow_elements
