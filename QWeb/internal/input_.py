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

from robot.api import logger
from QWeb.internal.exceptions import QWebElementNotFoundError, \
    QWebInstanceDoesNotExistError
from QWeb.internal import element, text, frame, javascript, util
from QWeb.internal.table import Table
from QWeb.internal.config_defaults import CONFIG


def get_input_element_by_locator(locator: str, anchor: Union[str, int], **kwargs) -> WebElement:
    """Find input element.

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
    if locator.startswith("xpath=") or locator.startswith("//") or locator.startswith("(//"):
        if locator.startswith("xpath="):
            xpath = locator.split("=", 1)[1]
        else:
            xpath = locator
        input_element = element.get_unique_element_by_xpath(xpath, index=anchor, **kwargs)
    else:  # Search using text
        input_xpath = CONFIG["MatchingInputElement"].format(locator)
        input_elements = element.get_webelements_in_active_area(input_xpath, **kwargs)
        if not input_elements:  # Find input element using locator
            locator_element = text.get_text_using_anchor(locator, str(anchor), **kwargs)
            input_elements = _get_all_input_elements()

            shadow_dom = CONFIG['ShadowDOM']
            if shadow_dom:
                shadow_inputs = element.get_all_inputs_from_shadow_dom()
                #  remove duplicates (normal search and including shadow search)
                input_elements = util.remove_duplicates_from_list(shadow_inputs, input_elements)

            input_element = element.get_closest_element(locator_element, input_elements)
        elif len(input_elements) == 1:
            input_element = input_elements[0]  # pylint: disable=unsubscriptable-object
        else:  # Found many
            input_element = text.get_element_using_anchor(input_elements, anchor, **kwargs)
    return input_element


def _get_all_input_elements() -> list[WebElement]:
    input_elements = element.get_webelements_in_active_area(CONFIG["AllInputElements"],
                                                            stay_in_current_frame=True)
    return input_elements


def get_input_elements_from_all_documents(
        locator: str,
        anchor: str,
        timeout: Union[int, float, str],  # pylint: disable=unused-argument
        index: Union[int, str] = 1,
        enable_check: bool = False,
        **kwargs) -> WebElement:
    """Function for finding input elements.
    Parameters
    ----------
    locator : str
       Label text or attribute that points to the checkbox.
    anchor : str
       in case there is duplicates.
    timeout : str
       How long we are finding before fail.
       Default = Search Strategy global default = 10 sec)
    index : int
       If table cell contains more than one input elements or if there is some kind of
       nested structure inside of given input index may needed. Default = 1 (first)
    enable_check : bool
        When CSS Selectors are used, we are not return disabled input element
        always by default. Element is needed with verify input status kw
        so if enable_check= True, disabled input_element is returned
    kwargs:
        limit_traverse : bool
            If set to false. We are heading up to fifth parent element if needed when
            finding relative input element for some label text.
    Returns
    -------
    WebElement
    """
    input_element: Optional[WebElement]
    index = int(index) - 1
    css = 'input:not([type="hidden"]):not([type="submit"]):not([type="button"])' \
          ':not([type="reset"]):not([type="checkbox"]):not([type="radio"])' \
          ':not([aria-hidden="true"]),' \
          'textarea:not([type="hidden"]),[contenteditable="true"]'
    kwargs['css'] = kwargs.get('css', css)
    if Table.is_table_coordinates(locator):
        table = Table.ACTIVE_TABLE.update_table()
        if table is None:
            raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
        locator_element = table.get_table_cell(locator, anchor)
        input_elements = element.get_element_from_childnodes(locator_element,
                                                             kwargs['css'],
                                                             dom_traversing=False)
        if input_elements:
            return input_elements[int(index)]
        raise QWebElementNotFoundError('No matching table input found')
    css_selector = CONFIG["CssSelectors"]
    if not css_selector or locator.startswith('xpath=') or locator.startswith('//'):
        input_element = get_input_element_by_locator(locator, index, **kwargs)
    else:
        logger.debug('Uses CSS-selectors to locate element')
        input_element = get_input_element_by_css_selector(locator, anchor, int(index), enable_check,
                                                          **kwargs)
        if not input_element:
            input_element = get_input_element_by_locator(locator, index, **kwargs)
    if input_element:
        if CONFIG['SearchMode']:
            element.draw_borders(input_element)
        return input_element
    raise QWebElementNotFoundError('No matching input elements found')


def get_input_element_by_css_selector(locator: str,
                                      anchor: str,
                                      index: int = 0,
                                      enable_check: bool = False,
                                      **kwargs) -> Optional[WebElement]:
    """Get input element using css selectors.
       Parameters
       ----------
       locator : str
           Label text or attribute that points to the input.
           Looking for placeholder and commonly used tooltip-attributes first.
           If locator is label text, finds input element by it's for attribute.
           if for attribute is not available, then finds element by doing some
           DOM traversing.
       anchor : str
           Text near the locator element or index. If placeholder or another
           direct attribute (title, tooltip, value) exists then anchor
           has to be index. Text is aloud when searching by label or some other
           text which is near to input element.
       index: int
            If multiple input elements is nested or in same table cell, index is needed.
       enable_check: bool
            If enable_check is set to true returns first match even if disabled one.
       Returns
       -------
       WebElement
       """
    input_element: Union[Optional[WebElement], list[WebElement]]
    partial_matches: list[WebElement] = []
    upload = kwargs.get('upload')
    if upload:
        try:
            index = int(locator) - 1
            kwargs['any_element'] = True
            input_elements = element.get_elements_by_attributes(**kwargs)
            if input_elements:
                return input_elements[index]
        except ValueError:
            logger.debug('locator was text')
    if 'qweb_old' not in kwargs:
        full_matches, partial_matches = get_input_elements_by_css(locator, **kwargs)

        if full_matches:
            full_matches = text.filter_by_modal_ancestor(full_matches)
            input_element = element.get_visible_elements_from_elements(full_matches, **kwargs)
            if input_element and str(anchor) == '1':
                input_element = input_element[index]
                return input_element
            if input_element:
                input_element = text.get_element_using_anchor(input_element, anchor, **kwargs)
                return input_element
    try:
        locator_element = text.get_text_using_anchor(locator, anchor, **kwargs)
        input_elements = list(
            dict.fromkeys(
                element.get_element_from_childnodes(locator_element, **kwargs) + partial_matches))
    except QWebElementNotFoundError:
        logger.trace('Element not found by visible text. Trying with partial match')
        input_elements = partial_matches
    if input_elements:
        input_elements = text.filter_by_modal_ancestor(input_elements)
        visibles = element.get_visible_elements_from_elements(input_elements, **kwargs)
        if visibles:
            if element.is_enabled(visibles[index]) or enable_check is True:
                return visibles[index]
    return None


@frame.all_frames
def get_inputs_including_shadow_dom(locator: str, **kwargs) -> list[WebElement]:
    web_elements = element.get_visible_elements_from_elements(
        javascript.get_all_input_elements_from_shadow_dom(), **kwargs)

    matches = javascript.get_by_attributes(web_elements, locator, False)
    full, partial = matches.get('full', []), matches.get('partial', [])
    shadow_elements = full + partial
    if shadow_elements:
        logger.debug(f'Found {len(shadow_elements)} inputs when extending search to shadow dom')
    return shadow_elements


def get_input_elements_by_css(locator: str, **kwargs):
    full_matches, partial_matches = element.get_elements_by_css(locator, **kwargs)

    shadow_dom = CONFIG['ShadowDOM']
    if shadow_dom:
        shadow_elements = get_inputs_including_shadow_dom(locator, **kwargs)
        #  remove duplicates (normal search and including shadow search)
        for el in shadow_elements:
            if full_matches is not None and el not in list(full_matches):
                full_matches.append(el)  # type: ignore[union-attr]
    return full_matches, partial_matches
