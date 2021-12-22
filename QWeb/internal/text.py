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

from selenium.common.exceptions import InvalidSelectorException, JavascriptException, \
    WebDriverException, NoSuchFrameException, NoSuchElementException
from robot.api import logger
from QWeb.internal import element, javascript, frame, util, browser
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebValueError,\
    QWebInstanceDoesNotExistError, QWebStalingElementError
from QWeb.internal.config_defaults import CONFIG


def get_element_by_locator_text(locator, anchor="1", index=1, **kwargs):
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
    except (QWebElementNotFoundError, InvalidSelectorException, JavascriptException,
            WebDriverException):
        try:
            web_element = element.get_unique_element_by_xpath(locator)
        except (QWebElementNotFoundError, InvalidSelectorException, NoSuchFrameException) as e:
            no_raise = util.par2bool(kwargs.get('allow_non_existent', False))
            if no_raise:
                return None
            raise QWebElementNotFoundError(e)
    if web_element:
        if 'parent' in kwargs and kwargs['parent']:
            tag_name = kwargs['parent']
            web_element = element.get_parent_element(
                web_element, tag_name)
        elif 'child' in kwargs and kwargs['child']:
            tag_name = kwargs['child']
            web_element = element.get_element_from_childnodes(
                web_element, tag_name, dom_traversing=False)[index]
        if CONFIG['SearchMode']:
            element.draw_borders(web_element)
        return web_element
    raise QWebElementNotFoundError('Element not found')


@frame.all_frames
def find_text(text):
    try:
        if javascript.execute_javascript(
                "return window.find('{}')".format(text.replace("\'", "\\'"))):
            return True
    except WebDriverException as e:
        logger.debug('Got webdriver exception from find text func: {}'.format(e))
    raise QWebElementNotFoundError('Text not found')


def get_text_elements(text, **kwargs):
    web_elements = None
    try:
        web_elements = _get_exact_text_element(text, **kwargs)
    except NoSuchFrameException:
        logger.debug('Got no such frame from get exact text')
    if util.par2bool(kwargs.get('partial_match', CONFIG['PartialMatch'])):
        try:
            web_elements = _get_contains_text_element(text, **kwargs)
        except NoSuchFrameException:
            logger.debug('Got no such frame from contains text')
    return web_elements


def get_unique_text_element(text, **kwargs):
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
    if web_elements and len(web_elements) == 1:
        return web_elements[0]
    raise QWebValueError('Text "{}" matched {} elements. Needs to be unique'
                         .format(text, len(web_elements)))


@frame.all_frames
def check_all_nodes(text, **kwargs):
    try:
        return element.get_visible_elements_from_elements(
            javascript.find_text_from_textnodes(text, **kwargs))
    except(WebDriverException, NoSuchFrameException, JavascriptException,
           QWebStalingElementError) as e:
        logger.info('Got {} from check all nodes'.format(e))
        return None


def get_all_text_elements(text, **kwargs):
    """Get all webelements found by text"""
    web_elements = []
    all_text_nodes = util.par2bool(kwargs.get('all_text_nodes', CONFIG['AllTextNodes']))
    kwargs['partial_match'] = kwargs.get('partial_match', CONFIG['PartialMatch'])
    if all_text_nodes:
        web_elements = check_all_nodes(text, **kwargs)
        if web_elements:
            return web_elements
    if 'css' not in kwargs:
        try:
            web_elements = get_clickable_element_by_js(text, **kwargs)
        except (JavascriptException, WebDriverException, NoSuchFrameException,
                QWebStalingElementError) as e:
            logger.debug('got {}. Syntax might be invalid'.format(e))
    if not web_elements:
        web_elements = get_text_elements(text, **kwargs)
    if not web_elements:
        raise QWebElementNotFoundError('Webpage did not contain text "{}"'.format(text))
    return web_elements


def get_text_using_anchor(text, anchor, **kwargs):
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
    modal_xpath = CONFIG['IsModalXpath']

    driver = browser.get_current_browser()
    if modal_xpath != "//body":
        # filter elements by modal (dialog etc)
        logger.debug("IsModalXpath filtering on, filtering...")
        modal_exists = driver.find_elements_by_xpath(modal_xpath)
        if modal_exists:
            web_elements = _filter_by_modal_ancestor(web_elements)
            logger.debug(f"after filtering there are: {len(web_elements)} matching elements")
            if not web_elements:
                raise QWebElementNotFoundError('Webpage did not contain text "{}"'.format(text))

    if len(web_elements) == 1:
        return web_elements[0]
    # Found many elements, use anchors to determine correct element
    correct_element = get_element_using_anchor(web_elements, anchor, **kwargs)
    return correct_element


def _get_exact_text_element(text, **kwargs):
    xpath = (CONFIG["TextMatch"].format(text))
    return element.get_webelements_in_active_area(xpath, **kwargs)


def _get_contains_text_element(text, **kwargs):
    xpath = (CONFIG["ContainingTextMatch"].format(text))
    return element.get_webelements_in_active_area(xpath, **kwargs)


def _filter_by_modal_ancestor(elements):
    xpath = CONFIG["IsModalXpath"]
    if xpath.startswith("//"):
        xpath = xpath[2:]

    logger.debug(f"length before filtering: {len(elements)}")
    elems_in_modal = []

    for elem in elements:
        try:
            elem.find_element_by_xpath(f"./../ancestor::{xpath}")
            elems_in_modal.append(elem)
        except NoSuchElementException:
            logger.debug("Filtering out element, modal open but not under modal")
            continue

    logger.debug(f"length after filtering: {len(elems_in_modal)}")
    return elems_in_modal


def get_element_using_anchor(elements, anchor, **kwargs):
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
            'Found {} elements. Use anchor to determine which is wanted'.format(len(elements)))
    # Select by index unless anchor type is text
    if anchor.isdigit() and kwargs.get("anchor_type", "auto").lower() != "text":
        anchor = int(anchor) - 1
        if anchor < len(elements):
            return elements[anchor]
        raise QWebInstanceDoesNotExistError('Found {} elements. Given anchor was {}'
                                            .format(len(elements), anchor + 1))
    if isinstance(anchor, str):  # Get closest element to anchor
        kwargs['stay_in_current_frame'] = True
        anchor_element = None
        if CONFIG['MultipleAnchors']:
            anchor_elements = []
            logger.debug('Multiple anchors enabled, trying to find first exact match')
            try:
                anchor_elements = _get_exact_text_element(anchor, **kwargs)
            except NoSuchFrameException:
                logger.debug('Got no such frame from get exact text')
            if len(anchor_elements) > 0:
                # Using first exact match as anchor
                anchor_element = anchor_elements[0]
            else:
                # No exact matches found, trying to find partial
                anchor_elements = get_text_elements(anchor, **kwargs)
                if len(anchor_elements) > 0:
                    logger.debug('No exact match found, using first partial match')
                    anchor_element = anchor_elements[0]
        else:
            anchor_element = get_unique_text_element(anchor, **kwargs)
        return element.get_closest_element(anchor_element, elements)
    raise TypeError("Unknown argument type {}".format(type(anchor)))


def get_item_using_anchor(text, anchor, **kwargs):
    xpath = '//*[@title="{0}" or @alt="{0}" or @data-tooltip="{0}" or ' \
            '@tooltip="{0}" or @aria-label="{0}" or @data-icon="{0}"]'.format(text)
    if CONFIG["CssSelectors"]:
        web_elements = _get_item_by_css(text, **kwargs)
    else:
        web_elements = element.get_webelements(xpath, **kwargs)
    if web_elements:
        if CONFIG['SearchMode']:
            element.draw_borders(_get_correct_element(web_elements, str(anchor)))
        return _get_correct_element(web_elements, str(anchor))
    no_raise = util.par2bool(kwargs.get('allow_non_existent', False))
    if no_raise:
        return None
    raise QWebElementNotFoundError('Cannot find item for locator {}'.format(text))


def _get_correct_element(web_elements, anchor):
    if len(web_elements) == 1:
        return web_elements[0]
    correct_element = get_element_using_anchor(
        web_elements, anchor)
    return correct_element


def _get_item_by_css(text, **kwargs):
    """
    Allows partial match. Anchor has to be number.
    :param text: str
        Attribute value of the element
    :return:
        webelement that containing attribute with given value
    """
    if 'partial_match' not in kwargs:
        kwargs['partial_match'] = True
    css = 'a, span, img, li, h1, h2, h3, h4, h5, h6, div, svg, p, button, input' \
          ':not([type="text"]):not([type="password"]):not([type="email"])'
    full, partial = element.get_elements_by_attributes(css, text, **kwargs)
    web_elements = element.get_visible_elements_from_elements(full + partial, **kwargs)
    if web_elements:
        return web_elements
    return None


@frame.all_frames
def get_clickable_element_by_js(locator, **kwargs):
    web_elements = element.get_visible_elements_from_elements(
        javascript.get_clickable(locator), **kwargs)
    if web_elements:
        logger.debug('Found elements by js: {}'.format(web_elements))
        return web_elements
    return None
