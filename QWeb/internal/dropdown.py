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
from typing import Union, Any, Optional
from robot.api import logger
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebInstanceDoesNotExistError
from QWeb.internal import text, element, javascript, util
from QWeb.internal.table import Table
from QWeb.internal.config_defaults import CONFIG


def get_dropdown_element_by_locator(locator: str, anchor: str) -> WebElement:
    """Find dropdown element.

    Parameters
    ----------
    locator : str
        Text that locates the input field. The input field that is closest
        to the text is selected. Also one can use xpath by adding xpath= prefix
        and then the xpath. Error is raised if the xpath matches to multiple
        elements.
    anchor : str
        Text near the input field's locator element. If the page contains
        many places where the locator is then anchor is used to get the
        one that is closest to it.
    """
    if locator.startswith("xpath=") or locator.startswith("//"):
        index = util.anchor_to_index(anchor)
        dropdown_element = element.get_unique_element_by_xpath(locator, index=index)
    else:  # Search using text
        # First we look through all select elements' options, matching locator
        matches = []
        elements = _get_all_dropdown_elements()

        shadow_dom = CONFIG['ShadowDOM']
        if shadow_dom:
            shadow_dropdowns = element.get_all_dropdowns_from_shadow_dom()
            #  remove duplicates (normal search and including shadow search)
            elements = util.remove_duplicates_from_list(shadow_dropdowns, elements)

        for dd_element in elements:
            options = [x.text for x in Select(dd_element).options]
            if locator in options:
                logger.debug("Found dropdown with options %s" % options)
                matches.append(dd_element)
        if matches:
            correct_element = text.get_element_using_anchor(matches, anchor)
            return correct_element

        # Then we try to find the element using attributes and text
        dropdown_xpath = (
            #  pylint: disable=line-too-long
            '//select[normalize-space(@placeholder)="{0}" or normalize-space(@value)="{0}" or  normalize-space(text())="{0}"]'
            .format(locator))
        dropdown_elements = element.get_webelements_in_active_area(dropdown_xpath)
        if len(dropdown_elements) == 1:
            dropdown_element = dropdown_elements[0]
        elif not dropdown_elements:  # Find dropdown element using locator
            locator_element = text.get_text_using_anchor(locator, anchor)
            dropdown_elements = _get_all_dropdown_elements(stay_in_current_frame=True)
            shadow_dom = CONFIG['ShadowDOM']
            if shadow_dom:
                shadow_dropdowns = element.get_all_dropdowns_from_shadow_dom()
                #  remove duplicates (normal search and including shadow search)
                dropdown_elements = util.remove_duplicates_from_list(shadow_dropdowns,
                                                                     dropdown_elements)
            dropdown_element = element.get_closest_element(locator_element, dropdown_elements)
        else:  # Found many
            logger.debug("found many, using anchor")
            dropdown_element = text.get_element_using_anchor(dropdown_elements, anchor)
    return dropdown_element


def get_dd_elements_from_all_documents(locator: str, anchor: str, index: Union[int, str],
                                       **kwargs: Any) -> Select:
    select: Optional[WebElement]
    if int(index) > 0:
        index = int(index) - 1
    css_selector = CONFIG["CssSelectors"]
    if not css_selector or locator.startswith('xpath=') or locator.startswith('//'):
        select = get_dropdown_element_by_locator(locator, anchor)
    elif Table.is_table_coordinates(locator):
        table = Table.ACTIVE_TABLE.update_table()
        if table is None:
            raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
        web_element = table.get_table_cell(locator, anchor)
        select = element.get_element_from_childnodes(web_element, 'select',
                                                     dom_traversing=False)[int(index)]
    else:
        select = get_dropdown_element_by_css_selector(locator, anchor, int(index), **kwargs)
    if not select:
        select = get_dropdown_element_by_locator(locator, anchor)
    if select:
        if CONFIG['SearchMode']:
            element.draw_borders(select)
        return Select(select)
    raise QWebElementNotFoundError('No matching elements found')


def get_dropdown_element_by_css_selector(locator: str, anchor: str, index: int,
                                         **kwargs: Any) -> Optional[WebElement]:
    """Get Dropdown element using css selectors.
       Parameters
       ----------
       locator : str
           Label text or attribute that points to the dropdown.
           Looking for placeholder and commonly used tooltip-attributes first.
           If locator is label text, finds input element by it's for attribute.
           if for attribute is not available, then finds element by doing some
           DOM traversing.
       anchor : str
           Using if locator is not an XPath.
       index : int
           If multiple elements use index to pick correct one.
       Returns
       -------
       WebElement
   """
    dropdown_elements = []
    partial_matches: list[WebElement] = []
    css = 'select'
    if 'qweb_old' not in kwargs:
        full_matches, partial_matches = element.get_elements_by_css(locator, css, **kwargs)
        if full_matches:
            if index != 0:
                try:
                    return full_matches[index]
                except IndexError as e:
                    raise QWebInstanceDoesNotExistError(
                        f'Found {len(full_matches)} elements. Given index was {index}') from e
            correct_element = text.get_element_using_anchor(full_matches, anchor)
            return correct_element
    try:
        locator_element = text.get_text_using_anchor(locator, anchor)
        # if this is option, return parent select immediately
        if locator_element.tag_name.lower() == "option":
            return javascript.execute_javascript("return arguments[0].parentNode;", locator_element)
        dropdown_elements = list(
            dict.fromkeys(
                element.get_element_from_childnodes(locator_element, css, **kwargs)
                + partial_matches))
    except QWebElementNotFoundError:
        logger.trace('Element not found by visible text. Trying with partial match')
        dropdown_elements = partial_matches
    if dropdown_elements:
        return dropdown_elements[index]
    return None


def _get_all_dropdown_elements(**kwargs: Any) -> list[WebElement]:
    dropdown_elements = element.get_webelements('//select', **kwargs)
    return dropdown_elements
