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
from QWeb.internal.exceptions import (
    QWebElementNotFoundError,
    QWebInstanceDoesNotExistError,
    QWebValueMismatchError,
)
from QWeb.internal import browser, element, text, frame, javascript, util
from QWeb.internal.table import Table
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.input_handler import INPUT_HANDLER as input_handler


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
            # search for only file type inputs if upload is set
            if kwargs.get("upload", False):
                input_elements = _get_all_input_elements('//input[@type="file"]')
            else:
                input_elements = _get_all_input_elements(CONFIG["AllInputElements"])

            shadow_dom = CONFIG["ShadowDOM"]
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


def _get_all_input_elements(xpath: str) -> list[WebElement]:
    return element.get_webelements_in_active_area(xpath, stay_in_current_frame=True)


def get_input_elements_from_all_documents(
    locator: str,
    anchor: str,
    timeout: Union[int, float, str],  # pylint: disable=unused-argument
    index: Union[int, str] = 1,
    enable_check: bool = False,
    **kwargs,
) -> WebElement:
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
    css = (
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"])'
        ':not([type="reset"]):not([type="checkbox"]):not([type="radio"])'
        ':not([aria-hidden="true"]),'
        'textarea:not([type="hidden"]),[contenteditable="true"]'
    )
    kwargs["css"] = kwargs.get("css", css)
    if Table.is_table_coordinates(locator):
        table = Table.ACTIVE_TABLE.update_table()
        if table is None:
            raise QWebInstanceDoesNotExistError("Table has not been defined with UseTable keyword")
        locator_element = table.get_table_cell(locator, anchor)
        input_elements = element.get_element_from_childnodes(
            locator_element, kwargs["css"], dom_traversing=False
        )
        if input_elements:
            return input_elements[int(index)]
        raise QWebElementNotFoundError("No matching table input found")
    css_selector = CONFIG["CssSelectors"]
    if not css_selector or locator.startswith("xpath=") or locator.startswith("//"):
        input_element = get_input_element_by_locator(locator, index, **kwargs)
    else:
        logger.debug("Uses CSS-selectors to locate element")
        input_element = get_input_element_by_css_selector(
            locator, anchor, int(index), enable_check, **kwargs
        )
        if not input_element:
            input_element = get_input_element_by_locator(locator, index, **kwargs)
    if input_element:
        if CONFIG["SearchMode"]:
            element.draw_borders(input_element)
        return input_element
    raise QWebElementNotFoundError("No matching input elements found")


def get_input_element_by_css_selector(
    locator: str, anchor: str, index: int = 0, enable_check: bool = False, **kwargs
) -> Optional[WebElement]:
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
    upload = kwargs.get("upload")
    if upload:
        try:
            file_index = int(locator) - 1
        except ValueError:
            logger.debug("locator was text")
        else:
            return get_file_input_element_by_index(file_index, **kwargs)
    if "qweb_old" not in kwargs:
        full_matches, partial_matches = get_input_elements_by_css(locator, **kwargs)
        # backup search via xpath. This is needed due to javascript search not reaching
        # all inputs under pseudo elements
        if not full_matches and not partial_matches:
            xpath = CONFIG["AllInputElements"]
            full_matches, partial_matches = element.get_elements_by_attributes(xpath, locator)

        if full_matches:
            full_matches = text.filter_by_modal_ancestor(full_matches)
            input_element = element.get_visible_elements_from_elements(full_matches, **kwargs)
            if input_element and str(anchor) == "1":
                input_element = input_element[index]
                return input_element
            if input_element:
                input_element = text.get_element_using_anchor(input_element, anchor, **kwargs)
                return input_element
    try:
        locator_element = text.get_text_using_anchor(locator, anchor, **kwargs)
        input_elements = list(
            dict.fromkeys(
                element.get_element_from_childnodes(locator_element, **kwargs) + partial_matches
            )
        )
    except QWebElementNotFoundError:
        logger.trace("Element not found by visible text. Trying with partial match")
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
        javascript.get_all_input_elements_from_shadow_dom(), **kwargs
    )

    matches = javascript.get_by_attributes(web_elements, locator, False)
    full, partial = matches.get("full", []), matches.get("partial", [])
    shadow_elements = full + partial
    if shadow_elements:
        logger.debug(f"Found {len(shadow_elements)} inputs when extending search to shadow dom")
    return shadow_elements


def _file_inputs_in_current_frame(**kwargs) -> list[WebElement]:
    """File inputs in the active frame document (driver must already be in that frame)."""
    shadow_dom = CONFIG["ShadowDOM"]
    if shadow_dom:
        elements = javascript.get_all_input_elements_from_shadow_dom("file")
    else:
        elements = javascript.get_all_elements('input[type="file"]')
    if not elements:
        return []
    elements = text.filter_by_modal_ancestor(elements)
    return element.get_visible_elements_from_elements(elements, **kwargs) or []


@frame.all_frames
def _find_file_input_by_global_index(**kwargs) -> Union[list[WebElement], WebElement]:
    """Per-frame file input list; frame walk uses pick_global_index to return one element."""
    return _file_inputs_in_current_frame(**kwargs)


def get_file_input_element_by_index(index: int, **kwargs) -> WebElement:
    """Return the file input at ``index`` (0-based) across frames in traversal order.

    Uses cumulative counts per frame and stops in the frame that contains the match so
    the driver stays in context for upload.
    """
    if index < 0:
        raise QWebElementNotFoundError("File input index must be >= 1 (1-based locator).")
    kwargs = dict(kwargs)
    if util.par2bool(kwargs.get("stay_in_current_frame", CONFIG["StayInCurrentFrame"])):
        elements = _file_inputs_in_current_frame(**kwargs)
        if index >= len(elements):
            raise QWebElementNotFoundError(
                "No file input at index {} (1-based). Found {} file input(s).".format(
                    index + 1, len(elements)
                )
            )
        return elements[index]

    # Cross-frame global index for @all_frames: pick_global_index is the 0-based input to
    # select; _pick_index_cum is a shared counter updated as each frame's file-input list is
    # seen (see frame._pick_global_index_from_list). Stop in the matching iframe for upload.
    # Set only on this kwargs copy — must not leak into unrelated frame/table searches.
    pick_cum = [0]
    kwargs["pick_global_index"] = index
    kwargs["_pick_index_cum"] = pick_cum
    result = _find_file_input_by_global_index(**kwargs)
    if isinstance(result, WebElement):
        return result
    raise QWebElementNotFoundError(
        "No file input at index {} (1-based). Found {} file input(s).".format(
            index + 1, pick_cum[0]
        )
    )


def get_input_elements_by_css(locator: str, **kwargs):
    full_matches, partial_matches = element.get_elements_by_css(locator, **kwargs)
    # return if we already get a full match
    if full_matches:
        return full_matches, partial_matches

    shadow_dom = CONFIG["ShadowDOM"]
    if shadow_dom:
        shadow_elements = get_inputs_including_shadow_dom(locator, **kwargs)
        #  remove duplicates (normal search and including shadow search)
        for el in shadow_elements:
            if full_matches is not None and el not in list(full_matches):
                full_matches.append(el)  # type: ignore[union-attr]
    return full_matches, partial_matches


def type_in_page(
    locator: str, input_text: str, anchor: str, index: int, missed: Optional[Exception], **kwargs
) -> None:
    """Type through a label XPath when ChromeDriver cannot return the input."""
    if missed is None:
        raise QWebElementNotFoundError("No matching input elements found")
    if element.looks_like_xpath(locator):
        _type_xpath_in_page(locator, input_text, index, missed, anchor=anchor, **kwargs)
        return
    anchor_text = _text_anchor(anchor)
    for xpath in _label_input_xpaths(locator, anchor_text, int(index)):
        if _type_one_xpath(xpath, input_text, 0, anchor_text, **kwargs):
            return
    raise missed


def _text_anchor(anchor: object) -> str:
    """Return anchor text. A numeric anchor selects by index and is not page text."""
    value = str(anchor or "")
    return "" if value.isdigit() else value


def _label_input_xpaths(locator: str, anchor_text: str, position: int) -> list[str]:
    """XPaths that resolve a visible label to its input."""
    quoted = util.escape_xpath_quotes(locator)
    text_is = f'normalize-space(translate(., "*", ""))={quoted}'
    label = f"(self::label or self::span) and {text_is}"
    if anchor_text:
        return [
            f"//label[{text_is}]/following::input[1]",
            f"//label[{text_is}]/following::textarea[1]",
            f"//*[{label}]/ancestor::*[.//input][1]//input[1]",
            f"//*[{label}]/ancestor::*[.//textarea][1]//textarea[1]",
        ]
    xpaths = _matching_input_xpath(locator)
    xpaths.extend(
        [
            f"(//label[{text_is}]/following::input)[{position}]",
            f"(//label[{text_is}]/following::textarea)[{position}]",
            f"(//*[{label}]/ancestor::*[.//input][1]//input)[{position}]",
            f"(//*[{label}]/ancestor::*[.//textarea][1]//textarea)[{position}]",
        ]
    )
    return xpaths


def _matching_input_xpath(locator: str) -> list[str]:
    try:
        return [str(CONFIG["MatchingInputElement"]).format(locator)]
    except (IndexError, KeyError, ValueError):
        return []


def _type_xpath_in_page(
    locator: str, input_text: str, index: int, missed: Optional[Exception], **kwargs
) -> None:
    """Type into an XPath match that ChromeDriver cannot return as a WebElement."""
    if not element.looks_like_xpath(locator):
        raise missed
    anchor_text = _text_anchor(kwargs.get("anchor"))
    if _type_one_xpath(locator, input_text, int(index) - 1, anchor_text, **kwargs):
        return
    raise missed


def _type_one_xpath(xpath: str, input_text: str, index: int, anchor_text: str, **kwargs) -> bool:
    key = kwargs.get("key", input_handler.line_break_key)
    send_tab = key == "\ue004"
    focused = element.xpath_in_page("focus", xpath, index, anchor=anchor_text)
    if focused is False:
        return False
    typed: Union[bool, str]
    if focused == "debug":
        typed = "debug"
    else:
        typed = _type_into_focused(xpath, input_text, index, anchor_text)
    if typed is False:
        return False
    check = util.par2bool(kwargs.get("check", CONFIG["CheckInputValue"]))
    expected = str(kwargs.get("expected", input_text))
    if check and str(typed) != expected:
        raise QWebValueMismatchError(f'Expected "{expected}" but field contained "{typed}"')
    if send_tab and focused != "debug":
        _press_tab(browser.get_current_browser(), xpath, index, anchor_text)
    return True


def _type_into_focused(
    xpath: str, input_text: str, index: int, anchor_text: str
) -> Union[bool, str]:
    """Type with real key events so a combo box opens its list."""
    driver = browser.get_current_browser()
    if _dispatch_text(driver, input_text):
        typed = element.xpath_in_page("value", xpath, index, anchor=anchor_text)
        if str(typed).strip() == input_text:
            return typed
    return element.xpath_in_page(
        "type", xpath, index, text=input_text, send_tab=False, anchor=anchor_text
    )


def _press_tab(driver: object, xpath: str, index: int, anchor_text: str) -> None:
    dispatch = getattr(driver, "execute_cdp_cmd", None)
    if dispatch is not None:
        try:
            _key_event(dispatch, "keyDown", "Tab", "Tab", 9, "")
            _key_event(dispatch, "keyUp", "Tab", "Tab", 9, "")
            return
        except Exception as error:  # pylint: disable=broad-exception-caught
            logger.debug("Tab dispatch failed: {}".format(error))
    element.xpath_in_page("tab", xpath, index, anchor=anchor_text)


def _dispatch_text(driver: object, characters: str) -> bool:
    """Send trusted key events. A value assignment does not open a combo box."""
    dispatch = getattr(driver, "execute_cdp_cmd", None)
    if dispatch is None:
        return False
    try:
        _hold_key(dispatch, "Control", "ControlLeft", 17, 2)
        _key_event(dispatch, "keyDown", "a", "KeyA", 65, "", 2)
        _key_event(dispatch, "keyUp", "a", "KeyA", 65, "", 2)
        _release_key(dispatch, "Control", "ControlLeft", 17)
        _key_event(dispatch, "keyDown", "Backspace", "Backspace", 8, "")
        _key_event(dispatch, "keyUp", "Backspace", "Backspace", 8, "")
        for char in characters:
            _key_event(dispatch, "keyDown", char, "", 0, char)
            _key_event(dispatch, "keyUp", char, "", 0, "")
    except Exception as error:  # pylint: disable=broad-exception-caught
        logger.debug("Key dispatch failed: {}".format(error))
        return False
    return True


def _hold_key(dispatch: object, key: str, code: str, codepoint: int, modifiers: int) -> None:
    _key_event(dispatch, "keyDown", key, code, codepoint, "", modifiers)


def _release_key(dispatch: object, key: str, code: str, codepoint: int) -> None:
    _key_event(dispatch, "keyUp", key, code, codepoint, "")


def _key_event(
    dispatch: object,
    phase: str,
    key: str,
    code: str,
    codepoint: int,
    key_text: str,
    modifiers: int = 0,
) -> None:
    dispatch(  # type: ignore[operator]
        "Input.dispatchKeyEvent",
        {
            "type": phase,
            "key": key,
            "code": code,
            "text": key_text,
            "unmodifiedText": key_text,
            "windowsVirtualKeyCode": codepoint,
            "nativeVirtualKeyCode": codepoint,
            "modifiers": modifiers,
        },
    )
