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

import math
from robot.api import logger
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, \
    StaleElementReferenceException, JavascriptException, InvalidSelectorException,\
    WebDriverException, NoSuchFrameException
from QWeb.internal import frame
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebStalingElementError,\
    QWebValueError, QWebSearchingMode
from QWeb.internal import browser, javascript, util
from QWeb.internal.config_defaults import CONFIG

ACTIVE_AREA_FUNCTION = None


def is_enabled(element):
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
    disabled = element.get_attribute('disabled')
    return not bool(disabled)


def is_readonly(element):
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
    return util.par2bool(javascript.execute_javascript(
        'return arguments[0].hasAttribute("readonly")', element))


def is_visible(element):
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
    visibility = javascript.execute_javascript('return arguments[0].style.display', element)
    return bool(visibility.lower() != 'none')


def get_closest_element(locator_element, candidate_elements):
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
        raise QWebElementNotFoundError('No elements visible')
    closest_element_list = []
    closest_distance = 1000000  # Just some large number
    for candidate_element in candidate_elements:
        element_info = _list_info(candidate_element)
        logger.debug("Measuring distance for: {}".format(element_info))
        if _overlap(locator_element, candidate_element):
            logger.debug('Elements overlap, returning this: {}'.format(element_info))
            return candidate_element
        distance = _calculate_closest_distance(locator_element,
                                               candidate_element)
        logger.debug("Candidate {}: distance: {}".format(candidate_element, distance))

        if abs(distance - closest_distance) < 2:
            closest_element_list.append(candidate_element)
            closest_distance = distance
        elif distance < closest_distance:
            closest_distance = distance
            closest_element_list = [candidate_element]

    closest_element = _get_closest_ortho_element(locator_element,
                                                 closest_element_list)

    logger.debug("Closest distance found is {}".format(closest_distance))
    logger.debug("Closest element is: {}".format(_list_info(closest_element)))
    return closest_element


def get_unique_element_by_xpath(xpath, **kwargs):
    """Get element if it is needed to be unique.

    One use case is that when xpath is written in the test script with
    the prefix xpath=.

    Parameters
    ----------
    xpath : str
        XPath string. If 'xpath=' -prefix is used, it will be omitted.
    """
    if xpath.startswith("xpath="):
        xpath = xpath.split("=", 1)[1]
    elements = get_webelements_in_active_area(xpath, **kwargs)
    # pylint: disable=no-else-return
    if elements and len(elements) == 1:
        if CONFIG['SearchMode']:
            draw_borders(elements[0])
        return elements[0]
    elif not elements:
        raise QWebElementNotFoundError(
            'XPath {} did not find any elements'.format(xpath))
    raise QWebValueError('XPath {} matched {} elements. Needs to be unique'
                         .format(xpath, len(elements)))


@frame.all_frames
def get_webelements(xpath, **kwargs):
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
    web_elements = driver.find_elements(By.XPATH, xpath)
    logger.trace("XPath {} matched {} WebElements"
                 .format(xpath, len(web_elements)))
    web_elements = get_visible_elements_from_elements(web_elements, **kwargs)
    return web_elements


@frame.all_frames
def get_webelements_in_active_area(xpath, **kwargs):
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
        active_area = ACTIVE_AREA_FUNCTION()
        if active_area:
            xpath = xpath.replace('//', './/', 1)
        else:
            driver = browser.get_current_browser()
            active_area = driver.find_element(By.XPATH, active_area_xpath)
    else:
        driver = browser.get_current_browser()
        try:
            active_area = driver.find_element(By.XPATH, active_area_xpath)
            if active_area is None:
                logger.debug('Got None for active area. Is page still loading '
                             'or is it missing body tag?')
                return None
        # //body not found, is page still loading? Return None to continue looping
        except NoSuchElementException:
            logger.debug("Cannot locate //body element. Is page still loading?")
            return None

    try:
        webelements = active_area.find_elements(By.XPATH, xpath)

        logger.trace('XPath {} matched {} webelements'
                     .format(xpath, len(webelements)))
        webelements = get_visible_elements_from_elements(webelements, **kwargs)
    except StaleElementReferenceException as se:
        raise QWebStalingElementError('Got StaleElementException') from se
    except (JavascriptException, InvalidSelectorException) as e:
        logger.debug('Got {}, returning None'.format(e))
        webelements = None
    return webelements


def get_visible_elements_from_elements(web_elements, **kwargs):
    visible_elements = []
    hiding_elements = []
    vis_check = util.par2bool(kwargs.get('visibility', CONFIG['Visibility']))
    if not vis_check:
        logger.debug('allow invisible elements')
        return web_elements
    viewport_check = util.par2bool(kwargs.get('viewport', CONFIG['InViewport']))
    try:
        elem_objects = javascript.get_visibility(web_elements)
        logger.debug('Checking visibility from all found elements: {}'.format(len(elem_objects)))
    except (JavascriptException, StaleElementReferenceException, TypeError) as e:
        raise QWebStalingElementError("Exception from visibility check: {}".format(e)) from e
    for el in elem_objects:
        onscreen = el.get('viewport')
        logger.debug('Is element in viewport: {}'.format(onscreen))
        css_visibility = el.get('css')
        logger.debug('CSS visibility is not hidden and '
                     'display is not none: {}'.format(css_visibility))
        offset = el.get('offset')
        logger.debug('Element offsetWidth is > 0: {}'.format(offset))
        if css_visibility and onscreen:
            if util.par2bool(kwargs.get('offset', CONFIG['OffsetCheck'])):
                if offset and onscreen:
                    visible_elements.append(el.get('elem'))
                elif offset:
                    hiding_elements.append(el.get('elem'))
            elif onscreen:
                visible_elements.append(el.get('elem'))
            else:
                hiding_elements.append(el.get('elem'))
        elif css_visibility:
            hiding_elements.append(el.get('elem'))
    logger.debug('found {} visible elements and {} hiding ones'
                 .format(len(visible_elements), len(hiding_elements)))
    if viewport_check:
        return visible_elements
    return visible_elements + hiding_elements


def get_all_inputs_from_shadow_dom():
    return javascript.get_all_input_elements_from_shadow_dom()


def draw_borders(elements):
    mode = CONFIG['SearchMode']
    color = CONFIG['HighlightColor']
    if not isinstance(elements, list):
        elements = [elements]
    for e in elements:
        if mode.lower() == 'debug':
            javascript.highlight_element(e, False, color=color)
            raise QWebSearchingMode('Element highlighted')
        if mode.lower() == 'draw':
            javascript.highlight_element(e, True, color=color)
        elif mode.lower() == 'flash':
            javascript.highlight_element(e, False, True, color=color)


def _calculate_closest_distance(element1, element2):
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
    closest_distance = 1000000  # Some large number
    for corner1 in corners_locations1:
        for corner2 in corners_locations2:
            distance = _manhattan_distance(corner1['x'], corner1['y'],
                                           corner2['x'], corner2['y'])
            if search_direction != 'closest':
                # y coordinate goes up downwards on page
                # small y is above
                angle = math.degrees(math.atan2(corner2['y'] - corner1['y'],
                                                corner2['x'] - corner1['x']))
            if search_direction == 'down':
                if not 5 < angle < 175:
                    logger.debug('Search direction is {} and element is not in arc'.
                                 format(search_direction))
                    distance = 1000000
            elif search_direction == 'up':
                if not -175 < angle < -5:
                    logger.debug('Search direction is {} and element is not in arc'.
                                 format(search_direction))
                    distance = 1000000
            elif search_direction == 'left':
                if not abs(angle) > 95:
                    logger.debug('Search direction is {} and element is not in arc'.
                                 format(search_direction))
                    distance = 1000000
            elif search_direction == 'right':
                if not -85 < angle < 85:
                    logger.debug('Search direction is {} and element is not in arc'.
                                 format(search_direction))
                    distance = 1000000
            if closest_distance > distance > 0:
                closest_distance = distance
    return closest_distance


def _calculate_closest_ortho_distance(element1, element2):
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
    distance_h = abs(center_1['x'] - center_2['x'])
    distance_v = abs(center_1['y'] - center_2['y'])
    return min(distance_h, distance_v)


def _get_center_location(element):
    """ Calculate rectangle's center locations

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
    center = {'x': location['x'] + (size['width'] / 2),
              'y': location['y'] + (size['height'] / 2)}
    return center


def _get_corners_locations(element):
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
    top_left_corner = {'x': location['x'], 'y': location['y']}
    top_right_corner = {'x': location['x'] + size['width'],
                        'y': location['y']}
    bottom_left_corner = {'x': location['x'],
                          'y': location['y'] + size['height']}
    bottom_right_corner = {'x': top_right_corner['x'],
                           'y': bottom_left_corner['y']}
    corners_locations = (top_left_corner, top_right_corner,
                         bottom_left_corner, bottom_right_corner)
    return corners_locations


def _manhattan_distance(x0, y0, x1, y1):
    """Get manhattan distance between points (x0, y0) and (x1, y1)."""
    return abs(x0 - x1) + abs(y0 - y1)


def _overlap(element1, element2):
    """Detects if two rectangles overlap
    """
    corners_locations1 = _get_corners_locations(element1)
    corners_locations2 = _get_corners_locations(element2)

    r1_left = min([i['x'] for i in corners_locations1])
    r1_right = max([i['x'] for i in corners_locations1])
    r1_top = max([i['y'] for i in corners_locations1])
    r1_bottom = min([i['y'] for i in corners_locations1])

    r2_left = min([i['x'] for i in corners_locations2])
    r2_right = max([i['x'] for i in corners_locations2])
    r2_top = max([i['y'] for i in corners_locations2])
    r2_bottom = min([i['y'] for i in corners_locations2])

    return _range_overlap(r1_left, r1_right, r2_left, r2_right) \
        and _range_overlap(r1_bottom, r1_top, r2_bottom, r2_top)


def _range_overlap(a_min, a_max, b_min, b_max):
    """Neither range is completely greater than the other
    """
    return (a_min <= b_max) and (b_min <= a_max)


def _get_closest_ortho_element(locator_element, element_list):
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

    closest_distance = 1000000
    for candidate_element in element_list:
        distance = _calculate_closest_ortho_distance(locator_element, candidate_element)
        logger.debug("Candidate {}: horizontal distance: {}".format(candidate_element,
                                                                    distance))
        if distance < closest_distance:
            closest_distance = distance
            closest_element = candidate_element

    return closest_element


def _list_info(candidate_element):
    """Log element id, title or placeholder
    """
    outer_html = candidate_element.get_attribute('outerHTML')
    if outer_html != '' or outer_html is not None:
        return "OuterHTML: {}".format(outer_html)
    return candidate_element


@frame.all_frames
def get_elements_by_attributes(css, locator=None, **kwargs):
    any_element = util.par2bool(kwargs.get('any_element', None))
    partial = util.par2bool(kwargs.get('partial_match', CONFIG['PartialMatch']))
    if 'tag' in kwargs:
        css = kwargs.get('tag')
    try:
        elements = javascript.get_all_elements(css)
        if any_element:
            return elements
        matches = javascript.get_by_attributes(elements, locator.replace("\'", "\\'"), partial)
        logger.debug('attrfunc found full matches: {}, partial matches: {}'
                     .format(matches.get('full'), matches.get('partial')))
        full, partial = matches.get('full'), matches.get('partial')
    except (WebDriverException, JavascriptException, AttributeError) as e:
        logger.debug('Got exception from get elements by attributes: {}'.format(e))
        full, partial = [], []
    if 'element_kw' not in kwargs:
        return full, partial
    web_elements = full + partial
    if web_elements:
        if CONFIG['SearchMode']:
            draw_borders(web_elements)
        return web_elements
    raise QWebElementNotFoundError('Element with {} attribute not found'.format(locator))


@frame.all_frames
def get_element_by_label_for(locator, css, **kwargs):  # pylint: disable=unused-argument
    partial = util.par2bool(kwargs.get('partial_match', CONFIG['PartialMatch']))
    limit = util.par2bool(kwargs.get('limit_traverse', CONFIG['LimitTraverse']))
    level = 3 if limit is True else 6
    try:
        matches = javascript.get_by_label(locator.replace("\'", "\\'"), css, level, partial)
        logger.debug('labelfunc found full matches: {}, partial matches: {}'
                     .format(matches.get('full'), matches.get('partial')))
        return matches.get('full'), matches.get('partial')
    except (WebDriverException, JavascriptException) as e:
        logger.warn('Exception from label func: {}'.format(e))
        return [], []


def get_element_from_childnodes(locator_element, css, dom_traversing=True, **kwargs):
    limit = util.par2bool(kwargs.get('limit_traverse', CONFIG['LimitTraverse']))
    level = 3 if limit is True else 6
    try:
        web_elements = get_visible_elements_from_elements(
            javascript.get_childnodes(locator_element, css, level, dom_traversing))
    except (WebDriverException, JavascriptException) as e:
        web_elements = None
        logger.debug('Got Exception from get_element_from_childnodes: {}'.format(e))
    if web_elements:
        return web_elements
    raise QWebElementNotFoundError('Child with tag {} not found.'.format(css))


def get_elements_by_css(locator, css, **kwargs):
    try:
        f0, p0 = get_elements_by_attributes(css, locator, **kwargs)
    except NoSuchFrameException:
        logger.debug('got no such frame exception from get elem bu attrs')
        f0, p0 = [], []
    if(len(f0 + p0)) > 0:
        kwargs['stay_in_current_frame'] = True
    try:
        f1, p1 = get_element_by_label_for(locator, css, **kwargs)
    except NoSuchFrameException:
        logger.debug('got no such frame exception from get elem by label')
        f1, p1 = [], []
    full_matches = list(dict.fromkeys(f0 + f1))
    partial_matches = list(dict.fromkeys(p0 + p1))
    return full_matches, partial_matches


def get_parent_element(web_element, tag):
    web_element = javascript.execute_javascript(
        'return arguments[0].closest(\'{}\')'.format(tag), web_element)
    if web_element:
        return web_element
    raise QWebElementNotFoundError('Parent with tag {} not found.'.format(tag))


def get_parent_list_element(locator_element, css):
    try:
        web_element = javascript.get_parent_list(locator_element, css)
    except (WebDriverException, JavascriptException) as e:
        web_element = None
        logger.debug('Got Exception from get_parent_list: {}'.format(e))
    if web_element:
        return web_element
    raise QWebElementNotFoundError('Parent with tag {} not found.'.format(css))


def get_element_to_click_from_list(active_list, index, **kwargs):
    if 'tag' in kwargs:
        element = javascript.execute_javascript(
            'return arguments[0].querySelector("{}")'.format(kwargs['tag']), active_list[index])
    else:
        element = active_list[index]
    return element
