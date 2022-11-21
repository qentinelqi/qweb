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
from typing import Optional, Any, Union
from selenium.webdriver.remote.webelement import WebElement

from robot.api import logger
from QWeb.internal.exceptions import QWebInstanceDoesNotExistError, QWebElementNotFoundError
from QWeb.internal import element, text, javascript, util
from QWeb.internal.table import Table
from QWeb.internal.config_defaults import CONFIG


def is_checked(checkbox_element: WebElement) -> bool:
    """Is checkbox checked.

    Parameters
    ----------
    checkbox_element : WebElement

    Returns
    -------
    bool
    """
    js = """
        var checked = function(el) {
            if (el.hasAttribute("aria-checked")) {
                return el.attributes["aria-checked"].value;
                console.log(el.attributes["aria-checked"].value);
            }
            return el.checked;
        }
        return checked(arguments[0]);
        """
    checked = util.par2bool(javascript.execute_javascript(js, checkbox_element))
    return bool(checked)


def get_checkbox_by_locator(locator: str, anchor: str) -> tuple[WebElement, None]:
    """Get checkbox element.

    Parameters
    ----------
    locator : str
        Either text that points to the checkbox or direct xpath to the
        checkbox. If using direct XPath then add prefix xpath=.
    anchor : str
        Using if locator is not an XPath.

    Returns
    -------
    WebElement
    """
    if locator.startswith("xpath=") or locator.startswith("//"):
        index = util.anchor_to_index(anchor)
        checkbox_element = element.get_unique_element_by_xpath(locator, index=index)
        # TODO: Check that the element is actually a checkbox
    else:  # No prefix given
        text_element = text.get_text_using_anchor(locator, anchor)
        xpath = '//input[@type="checkbox"]|//*[@role="checkbox"]'
        checkbox_elements = element.get_webelements_in_active_area(xpath,
                                                                   stay_in_current_frame=True)
        checkbox_element = element.get_closest_element(text_element, checkbox_elements)
    return checkbox_element, None


def get_checkbox_elements_from_all_documents(locator: str, anchor: str, index: Union[int, str],
                                             **kwargs: Any
                                             ) -> tuple[WebElement, Optional[WebElement]]:
    """Function for finding checkbox elements.
    Parameters
    ----------
    locator : str
        Label text or attribute that points to the checkbox.
    anchor : str
        in case there is duplicates.
    index : int
        If multiple matches. Use index to pick correct one.
    Returns
    -------
    WebElement
    """
    checkbox_element: Optional[WebElement]
    locator_element: Optional[WebElement]

    index = int(index) - 1
    css_selector = CONFIG["CssSelectors"]
    css = '[type="checkbox"], [role="checkbox"]'
    if Table.is_table_coordinates(locator):
        table = Table.ACTIVE_TABLE.update_table()
        if table is None:
            raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
        locator_element = table.get_table_cell(locator, anchor)
        checkbox_elements = element.get_element_from_childnodes(locator_element,
                                                                css,
                                                                dom_traversing=False,
                                                                **kwargs)
        if checkbox_elements:
            return checkbox_elements[index], locator_element
        raise QWebElementNotFoundError('No matching checkbox found')
    if not css_selector or locator.startswith('xpath=') or locator.startswith('//'):
        checkbox_element, locator_element = get_checkbox_by_locator(locator, anchor=anchor)
    else:
        checkbox_element, locator_element = get_checkbox_by_css_selector(locator,
                                                                         anchor=anchor,
                                                                         index=index,
                                                                         **kwargs)
        if not checkbox_element:
            checkbox_element, locator_element = get_checkbox_by_locator(locator, anchor)
    if checkbox_element:
        return checkbox_element, locator_element
    raise QWebElementNotFoundError('No matching element found')


def get_checkbox_by_css_selector(
        locator: str, anchor: str, index: int,
        **kwargs: Any) -> tuple[Optional[WebElement], Optional[WebElement]]:
    """Get checkbox using css selectors."""
    checkbox_elements = []
    partial_matches: list[WebElement] = []
    css = '[type="checkbox"], [role="checkbox"]'
    if 'qweb_old' not in kwargs:
        full_matches, partial_matches = element.get_elements_by_css(locator, css, **kwargs)
        if full_matches:
            checkbox_elements = element.get_visible_elements_from_elements(full_matches, **kwargs)
            if checkbox_elements:
                return checkbox_elements[index], None
    try:
        locator_element = text.get_text_using_anchor(locator, anchor)
        checkbox_elements = list(
            dict.fromkeys(
                element.get_element_from_childnodes(locator_element, css, **kwargs)
                + partial_matches))
        return checkbox_elements[index], locator_element
    except QWebElementNotFoundError:
        logger.trace('Element not found by visible text. Trying with partial match')
        checkbox_elements = partial_matches
    if checkbox_elements:
        logger.debug("Found element {}, index {}".format(checkbox_elements, index))
        return checkbox_elements[index], None
    return None, None
