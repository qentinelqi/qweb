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
from typing import Optional, Callable, Any, Union

import math
from robot.api import logger
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    JavascriptException,
    InvalidSelectorException,
    WebDriverException,
    NoSuchFrameException,
)
from QWeb.internal import frame
from QWeb.internal.exceptions import (
    QWebElementNotFoundError,
    QWebStalingElementError,
    QWebValueError,
    QWebSearchingMode,
)
from QWeb.internal import browser, javascript, util
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.page_node import PageNode, hold_xpath_matches

ACTIVE_AREA_FUNCTION: Optional[Callable[..., Any]] = None
DEFAULT_DISTANCE = 1000000.0  # Just some large number


def is_enabled(element: WebElement) -> bool:
    """Is the element interactable?

    Uses the disabled attribute to determine if form element is enabled or
    not.

    Parameters
    ----------
    element : WebElement

    Returns
    -------
    bool
    """
    disabled = element.get_attribute("disabled")
    return not bool(disabled)


def is_readonly(element: WebElement) -> bool:
    """Is the element interactable?

    Uses the readonly attribute to determine if form element is enabled or
    not.

    Parameters
    ----------
    element : WebElement

    Returns
    -------
    bool
    """
    return util.par2bool(
        javascript.execute_javascript('return arguments[0].hasAttribute("readonly")', element)
    )


def is_visible(element: WebElement) -> bool:
    """Is the element interactable?

    Uses the display attribute to determine if form element is visible or
    not.

    Parameters
    ----------
    element : WebElement

    Returns
    -------
    bool
    """
    visibility = javascript.execute_javascript("return arguments[0].style.display", element)
    return bool(visibility.lower() != "none")


def get_closest_element(
    locator_element: WebElement, candidate_elements: list[WebElement]
) -> WebElement:
    """Get the closest element in a list of elements to a wanted element.

    Parameters
    ----------
    locator_element : WebElement
    candidate_elements : :obj:`list` of :obj:`WebElement`

    Returns
    -------
    WebElement
    """
    if not candidate_elements:
        raise QWebElementNotFoundError("No elements visible")
    closest_element_list = []
    closest_distance = DEFAULT_DISTANCE
    for candidate_element in candidate_elements:
        element_info = _list_info(candidate_element)
        logger.debug("Measuring distance for: {}".format(element_info))
        if _overlap(locator_element, candidate_element):
            logger.debug("Elements overlap, returning this: {}".format(element_info))
            return candidate_element
        distance = _calculate_closest_distance(locator_element, candidate_element)
        logger.debug("Candidate {}: distance: {}".format(candidate_element, distance))

        if abs(distance - closest_distance) < 2:
            closest_element_list.append(candidate_element)
            closest_distance = distance
        elif distance < closest_distance:
            closest_distance = distance
            closest_element_list = [candidate_element]
    # if search direction is "forced" and closest distance is in default value
    # then we don't have the element on correct direction from the anchor
    enforce_direction = CONFIG.enforce_direction()
    if enforce_direction and closest_distance == DEFAULT_DISTANCE:
        logger.debug(f'No elements in expected direction {CONFIG.get_value("SearchDirection")}')
        raise QWebElementNotFoundError("No elements found in enforced direction")

    closest_element = _get_closest_ortho_element(locator_element, closest_element_list)

    logger.debug(f"Closest distance found is {closest_distance}")
    logger.debug(f"Closest element is: {_list_info(closest_element)}")
    return closest_element


def get_unique_element_by_xpath(
    xpath: str, index: Union[str, int] = 0, **kwargs: Any
) -> WebElement:
    """Get element if it is needed to be unique.

    One use case is that when xpath is written in the test script with
    the prefix xpath=.

    Parameters
    ----------
    xpath : str
        XPath string. If 'xpath=' -prefix is used, it will be omitted.
    index : int (Optional)
        Index of element to return if there are multiple.
    """
    if xpath.startswith("xpath="):
        xpath = xpath.split("=", 1)[1]
    try:
        index = int(index)
    except ValueError:
        index = 0
    elements = get_webelements_in_active_area(xpath, **kwargs)
    # pylint: disable=no-else-return
    if elements and len(elements) > index:
        if CONFIG["SearchMode"]:
            draw_borders(elements[index])
        return elements[index]
    elif not elements:
        raise QWebElementNotFoundError("XPath {} did not find any elements".format(xpath))
    raise QWebValueError(
        f"XPath {xpath} matched {len(elements)} elements." f"Used index was {index+1}"
    )


def looks_like_xpath(xpath: str) -> bool:
    """True when the locator is an XPath expression rather than visible text."""
    expression = xpath.split("=", 1)[1] if xpath.startswith("xpath=") else xpath
    return expression.startswith("//") or expression.startswith("(")


@frame.all_frames
def xpath_in_page(kind: str, xpath: str, index: int = 0, **kwargs: Any) -> Union[bool, str]:
    """Click, type, or confirm an XPath match without handing the node to ChromeDriver.

    document.evaluate can see nodes that ChromeDriver then marks stale, which
    discards the whole find result. The action stays in the page.
    """
    if xpath.startswith("xpath="):
        xpath = xpath.split("=", 1)[1]
    highlight = str(CONFIG["SearchMode"] or "")
    color = str(CONFIG["HighlightColor"] or "blue")
    found = javascript.xpath_action(
        kind,
        xpath,
        int(index),
        str(kwargs.get("text") or ""),
        highlight,
        color,
        bool(kwargs.get("send_tab", False)),
        str(kwargs.get("anchor") or ""),
        util.par2bool(kwargs.get("visibility", CONFIG["Visibility"])),
        util.par2bool(kwargs.get("offset", CONFIG["OffsetCheck"])),
        util.par2bool(kwargs.get("viewport", CONFIG["InViewport"])),
    )
    if found == "debug":
        raise QWebSearchingMode("Element highlighted")
    return found


def _matches_driver_cannot_wrap(driver: Any, xpath: str, **kwargs: Any) -> list[Any]:
    """Read XPath matches that the driver dropped or refused to wrap.

    document.evaluate can see a synthetic-shadow node. Returning that node makes
    ChromeDriver reject the whole result, so the node stays in the page.
    """
    try:
        wrapped = javascript.find_elements_in_page(driver, xpath)
    except (QWebStalingElementError, StaleElementReferenceException):
        wrapped = []
    if wrapped:
        return wrapped
    visibility = util.par2bool(kwargs.get("visibility", CONFIG["Visibility"]))
    offset = util.par2bool(kwargs.get("offset", CONFIG["OffsetCheck"]))
    viewport = util.par2bool(kwargs.get("viewport", CONFIG["InViewport"]))
    return hold_xpath_matches(xpath, visibility=visibility, offset=offset, viewport=viewport)


@frame.all_frames
def get_webelements(xpath: str, **kwargs: Any) -> list[WebElement]:
    """Get visible web elements that correspond to given XPath.

    To check that element is visible it is checked that it has width. This
    does not handle all cases but it is fast so no need to modify if it
    works. Replace the visibility check using WebElement's is_displayed
    method if necessary.

    Parameters
    ----------
    xpath : str
        XPath expression without xpath= prefix.

    Returns
    -------
    :obj:`list` of :obj:`WebElement`
        List of visible WebElements.
    """
    if xpath.startswith("xpath="):
        xpath = xpath.split("=", 1)[1]
    driver = browser.get_current_browser()
    dropped = False
    try:
        web_elements = javascript.find_elements_by_xpath(driver, xpath)
    except QWebStalingElementError as error:
        dropped = javascript.is_unwrapped_xpath_error(error)
        web_elements = []
    if not web_elements and dropped:
        web_elements = _matches_driver_cannot_wrap(driver, xpath, **kwargs)
    if web_elements and isinstance(web_elements[0], PageNode):
        logger.trace("XPath {} matched {} in-page nodes".format(xpath, len(web_elements)))
        return web_elements
    logger.trace("XPath {} matched {} WebElements".format(xpath, len(web_elements)))
    web_elements = get_visible_elements_from_elements(web_elements, **kwargs)

    return web_elements


@frame.all_frames
def get_webelements_by_css(css: str, **kwargs: Any) -> list[WebElement]:
    """Get visible web elements that correspond to given css selector.

    To check that element is visible it is checked that it has width. This
    does not handle all cases but it is fast so no need to modify if it
    works. Replace the visibility check using WebElement's is_displayed
    method if necessary.

    Parameters
    ----------
    css : str
        CSS selector to find the element.

    Returns
    -------
    :obj:`list` of :obj:`WebElement`
        List of visible WebElements.
    """
    driver = browser.get_current_browser()
    web_elements = driver.find_elements(By.CSS_SELECTOR, css)
    logger.debug("CSS selector {} matched {} WebElements".format(css, len(web_elements)))
    web_elements = get_visible_elements_from_elements(web_elements, **kwargs)
    return web_elements


@frame.all_frames
def get_webelements_in_active_area(xpath: str, **kwargs: Any) -> Optional[list[WebElement]]:
    """Find element under another element.

    If ${ACTIVE_AREA_FUNC} returns an element then the xpath is searched from
    that element. Otherwise the element is searched under body element.

    Parameters
    ----------
    xpath : str
        Xpath expression without xpath= prefix.

    Returns
    -------
    :obj:`list` of :obj:`WebElement`
        List of visible WebElements.
    """
    active_area_xpath = CONFIG["ActiveAreaXpath"]
    if ACTIVE_AREA_FUNCTION is not None:
        active_area = ACTIVE_AREA_FUNCTION()  # pylint:disable=E1102
        if active_area:
            xpath = xpath.replace("//", ".//", 1)
        else:
            driver = browser.get_current_browser()
            active_area = javascript.find_element_by_xpath(driver, active_area_xpath)
    else:
        driver = browser.get_current_browser()
        try:
            active_area = javascript.find_element_by_xpath(driver, active_area_xpath)
            if active_area is None:
                logger.debug(
                    "Got None for active area. Is page still loading  or is it missing body tag?"
                )
                return None
        # //body not found, is page still loading? Return None to continue looping
        except NoSuchElementException:
            logger.debug("Cannot locate //body element. Is page still loading?")
            return None

    try:
        webelements = javascript.find_elements_by_xpath(active_area, xpath)

        logger.trace("XPath {} matched {} webelements".format(xpath, len(webelements)))
        webelements = get_visible_elements_from_elements(webelements, **kwargs)
    except (StaleElementReferenceException, QWebStalingElementError) as se:
        if not javascript.is_unwrapped_xpath_error(se):
            if isinstance(se, StaleElementReferenceException):
                raise QWebStalingElementError("Got StaleElementException") from se
            raise
        # The driver dropped the XPath result. Evaluate that same expression in
        # the page and keep the nodes with the normal visibility rules.
        webelements = _in_page_matches(xpath, active_area, **kwargs)
    except (JavascriptException, InvalidSelectorException) as e:
        if javascript.is_unwrapped_xpath_error(e):
            webelements = _in_page_matches(xpath, active_area, **kwargs)
        else:
            logger.debug("Got {}, returning None".format(e))
            webelements = None
    return webelements


def _in_page_matches(
    xpath: str, context: Optional[WebElement] = None, **kwargs: Any
) -> list[Any]:
    """Same XPath and visibility rules, kept even when the driver cannot wrap them.

    querySelectorAll returns the nodes the driver accepts. A synthetic-shadow
    match is missing from that list, and substituting a parent the driver can
    wrap would be a different element. The match stays in the page instead.
    """
    driver = browser.get_current_browser()
    try:
        wrapped = javascript.find_elements_in_page(driver, xpath, context)
    except (QWebStalingElementError, StaleElementReferenceException, JavascriptException):
        wrapped = []
    if wrapped:
        return get_visible_elements_from_elements(wrapped, **kwargs)
    visibility = util.par2bool(kwargs.get("visibility", CONFIG["Visibility"]))
    offset = util.par2bool(kwargs.get("offset", CONFIG["OffsetCheck"]))
    viewport = util.par2bool(kwargs.get("viewport", CONFIG["InViewport"]))
    try:
        return hold_xpath_matches(
            xpath,
            visibility=visibility,
            offset=offset,
            viewport=viewport,
            context=context,
        )
    except (
        QWebStalingElementError,
        StaleElementReferenceException,
        InvalidSelectorException,
        JavascriptException,
    ):
        return []


def _keep_visible(
    web_elements: list[Any], elem_objects: list[dict], **kwargs: Any
) -> list[Any]:
    visible_elements = []
    hiding_elements = []
    viewport_check = util.par2bool(kwargs.get("viewport", CONFIG["InViewport"]))
    for element_ref, el in zip(web_elements, elem_objects):
        onscreen = el.get("viewport")
        logger.debug("Is element in viewport: {}".format(onscreen))
        css_visibility = el.get("css")
        logger.debug(
            "CSS visibility is not hidden and " "display is not none: {}".format(css_visibility)
        )
        offset = el.get("offset")
        logger.debug("Element offsetWidth is > 0: {}".format(offset))
        if css_visibility and onscreen:
            if util.par2bool(kwargs.get("offset", CONFIG["OffsetCheck"])):
                if offset and onscreen:
                    visible_elements.append(element_ref)
                elif offset:
                    hiding_elements.append(element_ref)
            elif onscreen:
                visible_elements.append(element_ref)
            else:
                hiding_elements.append(element_ref)
        elif css_visibility:
            hiding_elements.append(element_ref)
    logger.debug(
        "found {} visible elements and {} hiding ones".format(
            len(visible_elements), len(hiding_elements)
        )
    )
    if viewport_check:
        return visible_elements
    return visible_elements + hiding_elements


def get_visible_elements_from_elements(
    web_elements: list[WebElement], **kwargs: Any
) -> list[WebElement]:
    vis_check = util.par2bool(kwargs.get("visibility", CONFIG["Visibility"]))
    if not vis_check:
        logger.debug("allow invisible elements")
        return web_elements
    flags = _visibility_flags(web_elements)
    return _keep_visible(web_elements, flags, **kwargs)


def _visibility_flags(web_elements: list[Any]) -> list[dict]:
    """One visibility record per element, in the same order."""
    real_at = [i for i, item in enumerate(web_elements) if not isinstance(item, PageNode)]
    real_flags = _real_visibility_flags([web_elements[i] for i in real_at]) if real_at else []
    flags: list[dict] = []
    real_pos = 0
    for item in web_elements:
        if isinstance(item, PageNode):
            flags.append(item.shown_flags())
            continue
        flags.append(real_flags[real_pos])
        real_pos += 1
    return flags


def _real_visibility_flags(web_elements: list[Any]) -> list[dict]:
    try:
        info = javascript.get_visibility(web_elements)
        logger.debug("Checking visibility from all found elements: {}".format(len(info)))
        return list(info)
    except (JavascriptException, StaleElementReferenceException, TypeError) as error:
        if not javascript.is_unwrapped_xpath_error(error):
            raise QWebStalingElementError(
                "Exception from visibility check: {}".format(error)
            ) from error
    flags = []
    for web_element in web_elements:
        try:
            flags.extend(javascript.get_visibility([web_element]))
        except (JavascriptException, StaleElementReferenceException, TypeError) as item_error:
            if not javascript.is_unwrapped_xpath_error(item_error):
                raise QWebStalingElementError(
                    "Exception from visibility check: {}".format(item_error)
                ) from item_error
            # The driver already returned this node. Passing it back into a
            # script is what ChromeDriver rejects, so the size check cannot run.
            flags.append({"viewport": True, "css": True, "offset": True})
    return flags


def get_all_inputs_from_shadow_dom() -> list[WebElement]:
    return javascript.get_all_input_elements_from_shadow_dom()


def get_all_dropdowns_from_shadow_dom() -> list[WebElement]:
    return javascript.get_all_dropdown_elements_from_shadow_dom()


def draw_borders(elements: Union[WebElement, list[WebElement]]) -> None:
    mode = str(CONFIG["SearchMode"] or "")
    color = str(CONFIG["HighlightColor"] or "blue")
    if not isinstance(elements, list):
        elements = [elements]
    for e in elements:
        if isinstance(e, PageNode):
            if mode.lower() == "debug":
                e.mark(color, "debug")
                raise QWebSearchingMode("Element highlighted")
            if mode.lower() == "draw":
                e.mark(color, "draw")
            elif mode.lower() == "flash":
                e.mark(color, "flash")
            continue
        if mode.lower() == "debug":
            javascript.highlight_element(e, False, color=color)
            raise QWebSearchingMode("Element highlighted")
        if mode.lower() == "draw":
            javascript.highlight_element(e, True, color=color)
        elif mode.lower() == "flash":
            javascript.highlight_element(e, False, True, color=color)


def _calculate_closest_distance(element1: WebElement, element2: WebElement) -> float:
    """Calculate closest distance between elements in pixel units.

    Gets corners' locations for both elements and use them to calculate the
    closest distance between the elements.

    Uses Manhattan distance.

    Parameters
    ----------
    element1 : WebElement
    element2 : WebElement

    Returns
    -------
    float
    """
    search_direction = CONFIG["SearchDirection"]
    corners_locations1 = _get_corners_locations(element1)
    corners_locations2 = _get_corners_locations(element2)
    closest_distance = DEFAULT_DISTANCE
    for corner1 in corners_locations1:
        for corner2 in corners_locations2:
            distance = _manhattan_distance(corner1["x"], corner1["y"], corner2["x"], corner2["y"])
            if search_direction != "closest":
                # y coordinate goes up downwards on page
                # small y is above
                angle = math.degrees(
                    math.atan2(corner2["y"] - corner1["y"], corner2["x"] - corner1["x"])
                )

            if search_direction in ("down", "down!"):
                if not 5 < angle < 175:
                    logger.debug(
                        "Search direction is {} and element is not in arc".format(search_direction)
                    )
                    distance = DEFAULT_DISTANCE
            elif search_direction in ("up", "up!"):
                if not -175 < angle < -5:
                    logger.debug(
                        "Search direction is {} and element is not in arc".format(search_direction)
                    )
                    distance = DEFAULT_DISTANCE
            elif search_direction in ("left", "left!"):
                if not abs(angle) > 95:
                    logger.debug(
                        "Search direction is {} and element is not in arc".format(search_direction)
                    )
                    distance = DEFAULT_DISTANCE
            elif search_direction in ("right", "right!"):
                if not -85 < angle < 85:
                    logger.debug(
                        "Search direction is {} and element is not in arc".format(search_direction)
                    )
                    distance = DEFAULT_DISTANCE

            if closest_distance > distance > 0:
                closest_distance = distance
    return closest_distance


def _calculate_closest_ortho_distance(element1: WebElement, element2: WebElement) -> float:
    """Returns shortest ortho  distance between locator and candidate element centers

    Parameters
    ----------
    element1 : WebElement
    element2 : WebElement

    Returns
    -------
    float
    """
    center_1 = _get_center_location(element1)
    center_2 = _get_center_location(element2)
    distance_h = abs(center_1["x"] - center_2["x"])
    distance_v = abs(center_1["y"] - center_2["y"])
    return min(distance_h, distance_v)


def _get_center_location(element: WebElement) -> dict[str, float]:
    """Calculate rectangle's center locations

       Each element on a web page is in a rectangle. Uses the WebElement's
    location and size attributes to get center.

    Parameters
    ----------
    element : WebElement

    Returns
    -------
    tuple
        A tuple with 2 elements: center x and y coordinates.
    """
    location = element.location
    size = element.size
    center = {"x": location["x"] + (size["width"] / 2), "y": location["y"] + (size["height"] / 2)}
    return center


def _get_corners_locations(
    element: WebElement,
) -> tuple[dict[str, float], dict[str, float], dict[str, float], dict[str, float]]:
    """Calculate rectangle's corners' locations

    Each element on a web page is in a rectangle. Uses the WebElement's
    location and size attributes to get all corners.

    Parameters
    ----------
    element : WebElement

    Returns
    -------
    tuple
        A tuple with 4 elements: top left corner, top right corner, bottom
        left corner, bottom right corner.
    """
    location = element.location
    size = element.size
    top_left_corner = {"x": location["x"], "y": location["y"]}
    top_right_corner = {"x": location["x"] + size["width"], "y": location["y"]}
    bottom_left_corner = {"x": location["x"], "y": location["y"] + size["height"]}
    bottom_right_corner = {"x": top_right_corner["x"], "y": bottom_left_corner["y"]}
    corners_locations = (top_left_corner, top_right_corner, bottom_left_corner, bottom_right_corner)
    return corners_locations


def _manhattan_distance(x0: float, y0: float, x1: float, y1: float) -> float:
    """Get manhattan distance between points (x0, y0) and (x1, y1)."""
    return abs(x0 - x1) + abs(y0 - y1)


def _overlap(element1: WebElement, element2: WebElement) -> float:
    """Detects if two rectangles overlap"""
    corners_locations1 = _get_corners_locations(element1)
    corners_locations2 = _get_corners_locations(element2)

    # pylint: disable=R1728
    r1_left = min([i["x"] for i in corners_locations1])
    r1_right = max([i["x"] for i in corners_locations1])
    r1_top = max([i["y"] for i in corners_locations1])
    r1_bottom = min([i["y"] for i in corners_locations1])

    r2_left = min([i["x"] for i in corners_locations2])
    r2_right = max([i["x"] for i in corners_locations2])
    r2_top = max([i["y"] for i in corners_locations2])
    r2_bottom = min([i["y"] for i in corners_locations2])

    return _range_overlap(r1_left, r1_right, r2_left, r2_right) and _range_overlap(
        r1_bottom, r1_top, r2_bottom, r2_top
    )


def _range_overlap(a_min: float, a_max: float, b_min: float, b_max: float) -> float:
    """Neither range is completely greater than the other"""
    return (a_min <= b_max) and (b_min <= a_max)


def _get_closest_ortho_element(
    locator_element: WebElement, element_list: list[WebElement]
) -> WebElement:
    """Return closest element by orthogonal distance

    Compares all elements from a list against locator element based on their horizontal
    or vertical distance. Returns one that has shortest.

    Parameters
    ----------
    locator_element : WebElement
    element_list: list of WebElements

    Returns
    -------
    WebElement
    """
    list_len = len(element_list)
    # pylint: disable=no-else-return
    if list_len == 1:
        return element_list[0]
    elif list_len == 0:
        raise IndexError

    closest_distance = DEFAULT_DISTANCE
    for candidate_element in element_list:
        distance = _calculate_closest_ortho_distance(locator_element, candidate_element)
        logger.debug("Candidate {}: horizontal distance: {}".format(candidate_element, distance))
        if distance < closest_distance:
            closest_distance = distance
            closest_element = candidate_element

    return closest_element


def operator_verify(value: str, expected: str, operator: str) -> None:
    """verify value based on given operator / condition"""
    EQUALS = ["equal", "equals", "=="]
    NOT_EQUAL = ["not equal", "!="]
    LESS_THAN = ["less than", "<"]
    GREATER_THAN = ["greater than", ">"]
    LESS_THAN_OR_EQUAL = ["less than or equal", "<="]
    GREATER_THAN_OR_EQUAL = ["greater than or equal", ">="]

    valid_operators = []
    valid_operators.extend(EQUALS)
    valid_operators.extend(NOT_EQUAL)
    valid_operators.extend(LESS_THAN)
    valid_operators.extend(GREATER_THAN)
    valid_operators.extend(LESS_THAN_OR_EQUAL)
    valid_operators.extend(GREATER_THAN_OR_EQUAL)
    valid_operators.append("contains")
    valid_operators.append("not contains")

    operator = operator.lower()

    if operator not in valid_operators:
        raise QWebValueError(
            f'Incorrect operator "{operator}" given. Supported operators are:'
            f'"{valid_operators}"'
        )

    if operator in EQUALS and value != expected:
        raise QWebValueError(
            f"Expected attribute value differs from real value: {expected}/{value}"
        )
    if operator in NOT_EQUAL and value == expected:
        raise QWebValueError(f"Expected attribute value matches real value: {expected}/{value}")
    if operator == "contains" and expected not in value:
        raise QWebValueError(f'Attribute value "{value}" does not contain: "{expected}"')
    if operator == "not contains" and expected in value:
        raise QWebValueError(f'Attribute value "{value}" contains: "{expected}"')

    # numeric comparison operator used but either value not numeric
    if [
        x
        for x in [GREATER_THAN, LESS_THAN, LESS_THAN_OR_EQUAL, GREATER_THAN_OR_EQUAL]
        if operator in x
    ]:
        if not (value.isdigit() and expected.isdigit()):
            raise QWebValueError(f'Attribute value "{value}" is not numeric!')

    if operator in GREATER_THAN and int(value) <= int(expected):
        raise QWebValueError(
            f'Attribute value: "{value}" is not greater than expected: "{expected}"'
        )

    if operator in LESS_THAN and int(value) >= int(expected):
        raise QWebValueError(f'Attribute value: "{value}" is greater than expected: "{expected}"')
    if operator in GREATER_THAN_OR_EQUAL and int(value) < int(expected):
        raise QWebValueError(
            f'Attribute value: "{value}" is not greater or equal than expected: "{expected}"'
        )
    if operator in LESS_THAN_OR_EQUAL and int(value) > int(expected):
        raise QWebValueError(
            f'Attribute value: "{value}" is not less or equal than expected: "{expected}"'
        )


def _list_info(candidate_element):
    """Log element id, title or placeholder"""
    outer_html = candidate_element.get_attribute("outerHTML")
    if outer_html != "" or outer_html is not None:
        return "OuterHTML: {}".format(outer_html)
    return candidate_element


def _plain_tag_list(css: str) -> bool:
    """True for ``a`` or ``a, span``. A selector such as ``input:not(...)`` is not."""
    pieces = [piece.strip() for piece in css.split(",") if piece.strip()]
    if not pieces:
        return False
    return all(piece.replace("-", "").isalnum() for piece in pieces)


def _attribute_xpath(css: str, locator: str, partial: bool) -> str:
    """XPath for tags whose any attribute matches, instead of every tag on the page."""
    tags = []
    for piece in css.split(","):
        name = piece.strip()
        if name and name.replace("-", "").isalnum():
            tags.append(name)
    if not tags:
        return "//*"
    quoted = util.escape_xpath_quotes(locator.strip())
    if partial:
        test = f"contains(normalize-space(.), {quoted})"
    else:
        test = f"normalize-space(.)={quoted}"
    return " | ".join(f"//{tag}[@*[{test}]]" for tag in tags)


def _fallback_xpath(css: str, locator: Optional[str], partial: bool, xpath_search: bool) -> str:
    if xpath_search:
        return css
    # ClickItem tag=a looks up that attribute directly. An input selector is a
    # different search: turning it into "any input with this attribute" types
    # into a field that merely contains the label text.
    if locator and _plain_tag_list(css):
        return _attribute_xpath(css, locator, partial)
    return f"//{css}"


@frame.all_frames
def get_elements_by_attributes(
    css: str, locator: Optional[str] = None, **kwargs
) -> Union[list[WebElement], tuple[list[WebElement], list[WebElement]]]:
    any_element = util.par2bool(kwargs.get("any_element", ""))
    partial = util.par2bool(kwargs.get("partial_match", CONFIG["PartialMatch"]))
    if "tag" in kwargs:
        css = str(kwargs.get("tag"))
    try:
        xpath_search = css.startswith("xpath=") or css.startswith("//")
        if not xpath_search:
            elements = javascript.get_all_elements(css)
            if any_element:
                return elements
            matches = javascript.get_by_attributes(
                elements,
                locator.replace("'", "\\'"),  # type: ignore[union-attr]
                partial,
            )
        else:
            matches = {"full": [], "partial": []}

        # try with xpath if no matches and tag is givenor if css contains xpath
        # there have been few cases where css search doesn't work
        if len(matches.get("full", [])) == 0 and len(matches.get("partial", [])) == 0:
            try:
                xpath = _fallback_xpath(css, locator, partial, xpath_search)
                driver = browser.get_current_browser()
                elements = javascript.find_elements_by_xpath(driver, xpath)

                matches = javascript.get_by_attributes(
                    elements,
                    locator.replace("'", "\\'"),  # type: ignore[union-attr]
                    partial,
                )
            except InvalidSelectorException:
                matches = {"full": [], "partial": []}

        logger.debug(
            "attrfunc found full matches: {}, partial matches: {}".format(
                matches.get("full", []), matches.get("partial", [])
            )
        )
        full_matches, partial_matches = matches.get("full", []), matches.get("partial", [])
    except (WebDriverException, JavascriptException, AttributeError) as e:
        logger.debug("Got exception from get elements by attributes: {}".format(e))
        full_matches, partial_matches = [], []

    if "element_kw" not in kwargs:
        return full_matches, partial_matches
    web_elements = full_matches + partial_matches

    if web_elements:
        if CONFIG["SearchMode"]:
            draw_borders(web_elements)
        return web_elements
    raise QWebElementNotFoundError("Element with {} attribute not found".format(locator))


@frame.all_frames
def get_element_by_label_for(
    locator: str, css: str, **kwargs
) -> tuple[list[WebElement], list[WebElement]]:  # pylint: disable=unused-argument
    partial = util.par2bool(kwargs.get("partial_match", CONFIG["PartialMatch"]))
    limit = util.par2bool(kwargs.get("limit_traverse", CONFIG["LimitTraverse"]))
    level = 3 if limit is True else 6
    try:
        matches = javascript.get_by_label(locator.replace("'", "\\'"), css, level, partial)
        logger.debug(
            "labelfunc found full matches: {}, partial matches: {}".format(
                matches.get("full", []), matches.get("partial", [])
            )
        )
        return matches.get("full", []), matches.get("partial", [])
    except (WebDriverException, JavascriptException) as e:
        logger.warn("Exception from label func: {}".format(e))
        return [], []


def get_element_from_childnodes(
    locator_element: WebElement, css: str, dom_traversing: bool = True, **kwargs
) -> list[WebElement]:
    limit = util.par2bool(kwargs.get("limit_traverse", CONFIG["LimitTraverse"]))
    level = 3 if limit is True else 6
    try:
        web_elements = get_visible_elements_from_elements(
            javascript.get_childnodes(locator_element, css, level, dom_traversing)
        )
    except (WebDriverException, JavascriptException) as e:
        web_elements = None
        logger.debug("Got Exception from get_element_from_childnodes: {}".format(e))
    # if all else fails, try to find children with xpath
    if not web_elements:
        try:
            web_elements = javascript.find_elements_by_xpath(locator_element, f".//{css}")
        except InvalidSelectorException:
            web_elements = None
    if web_elements:
        return web_elements
    raise QWebElementNotFoundError("Child with tag {} not found.".format(css))


def get_elements_by_css(
    locator: str, css: str, **kwargs
) -> tuple[list[WebElement], list[WebElement]]:
    try:
        f0, p0 = get_elements_by_attributes(css, locator, **kwargs)
    except NoSuchFrameException:
        logger.debug("got no such frame exception from get elem bu attrs")
        f0, p0 = [], []
    if (len(f0 + p0)) > 0:
        kwargs["stay_in_current_frame"] = True
    try:
        f1, p1 = get_element_by_label_for(locator, css, **kwargs)
    except NoSuchFrameException:
        logger.debug("got no such frame exception from get elem by label")
        f1, p1 = [], []
    full_matches = list(dict.fromkeys(f0 + f1))
    partial_matches = list(dict.fromkeys(p0 + p1))
    return full_matches, partial_matches


def get_parent_element(web_element: WebElement, tag: str) -> WebElement:
    web_element = javascript.execute_javascript(
        "return arguments[0].closest('{}')".format(tag), web_element
    )
    if web_element:
        return web_element
    raise QWebElementNotFoundError("Parent with tag {} not found.".format(tag))


def get_parent_list_element(locator_element: WebElement, css: str) -> WebElement:
    try:
        web_element = javascript.get_parent_list(locator_element, css)
    except (WebDriverException, JavascriptException) as e:
        web_element = None
        logger.debug("Got Exception from get_parent_list: {}".format(e))
    if isinstance(web_element, WebElement):
        return web_element
    raise QWebElementNotFoundError("Parent with tag {} not found.".format(css))


def get_element_to_click_from_list(
    active_list: list[WebElement], index: int, **kwargs
) -> WebElement:
    if "tag" in kwargs:
        element = javascript.execute_javascript(
            'return arguments[0].querySelector("{}")'.format(kwargs["tag"]), active_list[index]
        )
    else:
        element = active_list[index]
    return element


def get_element_by_index(elements: list[WebElement], index: Union[str, int]) -> WebElement:
    if str(index).isdigit():
        try:
            return elements[int(index) - 1]
        except IndexError as ie:
            raise QWebValueError(
                f'Only "{len(elements)}" elements found.' f'Used index was "{index}"'
            ) from ie
    raise ValueError(f'Index should be numeric. Used index was: "{index}"')
