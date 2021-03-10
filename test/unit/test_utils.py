# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------

from QWeb.internal.util import get_substring, set_line_break, prefs_to_dict, xpath_validator,\
    par2bool
from QWeb.internal.exceptions import QWebValueMismatchError
from unittest.mock import patch
import pytest


class Mocker123:
    capabilities = {'browserName': 'firefox'}


@patch('QWeb.internal.util.browser.get_current_browser')
def test_set_line_break(patched_browser):
    patched_browser.return_value = Mocker123()
    result = set_line_break('\ue000')
    assert result == ''


def test_get_substring():
    assert get_substring('9\xa0700') == '9 700'
    assert get_substring('42 02,00', float=True) == 4202.00
    assert get_substring('333 44', int=True) == 33344
    assert isinstance(get_substring('42 02,00', int=True), int)
    assert isinstance(get_substring('42 02,00', float=True), float)
    with pytest.raises(QWebValueMismatchError):
        get_substring('foobar', float=True)
    with pytest.raises(QWebValueMismatchError):
        get_substring('foobar', int=True)


def test_prefs_to_dict():
    expected_result = {'key1': 'value1',
                       'key2': 'value2',
                       'key3': 'value3'
                       }
    assert prefs_to_dict('"key1":"value1", "key2":"value2", "key3":"value3"') == expected_result
    assert prefs_to_dict('key1: value1, key2:value2, key3:value3') == expected_result
    assert prefs_to_dict(expected_result) == expected_result


def test_par2bool():
    should_return_true = ["TRue", "1", "ON", True, 1]
    for x in should_return_true:
        assert par2bool(x) is True
    assert par2bool('False') is False


def test_xpath_validator():
    xpaths = ["xpath=//div[@bar='bar']", "//div[@bar='bar']", "/html/body/table[1]"]
    for x in xpaths:
        assert xpath_validator(x) is True
    assert xpath_validator("div[@bar='bar']") is False
