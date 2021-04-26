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

import pytest
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebValueError
from QWeb.internal.element import _overlap, \
                                  _get_closest_ortho_element, \
                                  get_closest_element, \
                                  get_unique_element_by_xpath
from unittest.mock import patch, MagicMock


@patch('QWeb.internal.element._get_corners_locations')
def test_no_overlap(patch_corners):
    c1 = ({'x': 10, 'y': 10}, {'x': 20, 'y': 10},
          {'x': 10, 'y': 20}, {'x': 20, 'y': 20})
    c2 = ({'x': 30, 'y': 30}, {'x': 40, 'y': 30},
          {'x': 30, 'y': 40}, {'x': 40, 'y': 40})
    patch_corners.side_effect = [c1, c2]
    assert not _overlap(None, None)


@patch('QWeb.internal.element._get_corners_locations')
def test_overlap_side(patch_corners):
    c1 = ({'x': 10, 'y': 15}, {'x': 20, 'y': 15},
          {'x': 10, 'y': 20}, {'x': 20, 'y': 20})
    c2 = ({'x': 15, 'y': 10}, {'x': 40, 'y': 10},
          {'x': 15, 'y': 30}, {'x': 40, 'y': 30})
    patch_corners.side_effect = [c1, c2]
    assert _overlap(None, None)


@patch('QWeb.internal.element._get_corners_locations')
def test_overlap_corner(patch_corners):
    c1 = ({'x': 10, 'y': 10}, {'x': 20, 'y': 10},
          {'x': 10, 'y': 20}, {'x': 20, 'y': 20})
    c2 = ({'x': 15, 'y': 15}, {'x': 40, 'y': 15},
          {'x': 15, 'y': 30}, {'x': 40, 'y': 30})
    patch_corners.side_effect = [c1, c2]
    assert _overlap(None, None)


@patch('QWeb.internal.element._get_corners_locations')
def test_inside(patch_corners):
    c1 = ({'x': 10, 'y': 10}, {'x': 20, 'y': 10},
          {'x': 10, 'y': 20}, {'x': 20, 'y': 20})
    c2 = ({'x': 15, 'y': 15}, {'x': 18, 'y': 15},
          {'x': 15, 'y': 18}, {'x': 18, 'y': 18})
    patch_corners.side_effect = [c1, c2]
    assert _overlap(None, None)


@patch('QWeb.internal.element._get_center_location')
def test_get_closest_parallel_element(patch_center):
    c1 = {'x': 10, 'y': 10}
    c2 = {'x': 12, 'y': 10}
    c3 = {'x': 12, 'y': 12}
    patch_center.side_effect = [c1, c2, c1, c3]
    assert _get_closest_ortho_element('mock1', ['mock2', 'mock3']) == 'mock2'


def test_no_visible_elements():
    with pytest.raises(QWebElementNotFoundError):
        get_closest_element('', [])


def test_get_closest_element_one_candidate():
    locator_element = MagicMock()
    locator_element.location = {'x': 28, 'y': 328}
    locator_element.size = {'width': 337, 'height': 31}
    locator_element.get_attribute.return_value = 'foo'

    cand1 = MagicMock()
    cand1.location = {'x': 370, 'y': 332}
    cand1.size = {'width': 96, 'height': 22}
    cand1.get_attribute.return_value = 'foo'

    assert get_closest_element(locator_element, [cand1]) == cand1


def test_get_closest_element_two_candidates():
    locator_element = MagicMock()
    locator_element.location = {'x': 28, 'y': 328}
    locator_element.size = {'width': 337, 'height': 31}
    locator_element.get_attribute.return_value = 'foo'

    cand1 = MagicMock()
    cand1.location = {'x': 370, 'y': 332}
    cand1.size = {'width': 96, 'height': 22}
    cand1.get_attribute.return_value = 'foo'

    cand2 = MagicMock()
    cand2.location = {'x': 370, 'y': 432}
    cand2.size = {'width': 96, 'height': 22}
    cand2.get_attribute.return_value = 'foo'

    assert get_closest_element(locator_element, [cand1, cand2]) == cand1
    assert get_closest_element(locator_element, [cand2, cand1]) == cand1


def test_get_closest_element_rounding_simulate_py2_rounding():
    '''Chromedriver gives element coordinates with one decimal
       precision like x: 28.5. Selenium rounds these to integer.
       This rounding causes uncertainty when calculating the closest
       element. Also, rounding function was changed in Py3 and
       it now uses banker's rounding where it rounds to even number.

       These two tests simulate real life case where Python 2 worked but
       Python 3 did not. I have modified get_closest_element function
       to handle elements with similar distances as if they are same.
    '''
    locator_element = MagicMock()
    locator_element.location = {'x': 29, 'y': 328}
    locator_element.size = {'width': 337, 'height': 31}
    locator_element.get_attribute.return_value = 'foo'

    cand1 = MagicMock()
    cand1.location = {'x': 370, 'y': 302}
    cand1.size = {'width': 96, 'height': 22}
    cand1.get_attribute.return_value = 'foo'

    cand2 = MagicMock()
    cand2.location = {'x': 370, 'y': 332}
    cand2.size = {'width': 96, 'height': 22}
    cand2.get_attribute.return_value = 'foo'

    cand3 = MagicMock()
    cand3.location = {'x': 370, 'y': 363}
    cand3.size = {'width': 96, 'height': 22}
    cand3.get_attribute.return_value = 'foo'

    assert get_closest_element(locator_element, [cand1, cand2, cand3]) == cand2
    assert get_closest_element(locator_element, [cand1, cand3, cand2]) == cand2
    assert get_closest_element(locator_element, [cand3, cand1, cand2]) == cand2


def test_get_closest_element_rounding_simulate_py3_rounding():
    locator_element = MagicMock()
    locator_element.location = {'x': 28, 'y': 328}
    locator_element.size = {'width': 337, 'height': 31}
    locator_element.get_attribute.return_value = 'foo'

    cand1 = MagicMock()
    cand1.location = {'x': 370, 'y': 302}
    cand1.size = {'width': 96, 'height': 22}
    cand1.get_attribute.return_value = 'foo'

    cand2 = MagicMock()
    cand2.location = {'x': 370, 'y': 332}
    cand2.size = {'width': 96, 'height': 22}
    cand2.get_attribute.return_value = 'foo'

    cand3 = MagicMock()
    cand3.location = {'x': 370, 'y': 362}
    cand3.size = {'width': 96, 'height': 22}
    cand3.get_attribute.return_value = 'foo'

    assert get_closest_element(locator_element, [cand1, cand2, cand3]) == cand2
    assert get_closest_element(locator_element, [cand1, cand3, cand2]) == cand2
    assert get_closest_element(locator_element, [cand3, cand1, cand2]) == cand2


@patch('QWeb.internal.element.get_webelements_in_active_area')
def test_get_unique_element_by_xpath_positives(patch_webelements):
    xpath1 = "xpath=//div[@bar='bar']"
    xpath2 = "//div[@bar='bar']"
    patch_webelements.return_value = ['test123']
    assert get_unique_element_by_xpath(xpath1) == 'test123'
    assert get_unique_element_by_xpath(xpath2) == 'test123'


@patch('QWeb.internal.element.get_webelements_in_active_area')
def test_get_unique_element_by_xpath_negatives(patch_webelements):
    xpath = "xpath=//div[@bar='bar']"
    patch_webelements.return_value = ['test123', 'test666']
    with pytest.raises(QWebValueError):
        get_unique_element_by_xpath(xpath)

    patch_webelements.return_value = []
    with pytest.raises(QWebElementNotFoundError):
        get_unique_element_by_xpath(xpath)


@patch('QWeb.internal.element.get_webelements_in_active_area')
def test_get_unique_element_by_xpath_none(patch_webelements):
    xpath = "xpath=//div[@bar='bar']"
    patch_webelements.return_value = None
    with pytest.raises(QWebElementNotFoundError):
        get_unique_element_by_xpath(xpath)
