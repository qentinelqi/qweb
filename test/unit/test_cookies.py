# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------

from QWeb.internal import cookies
from unittest.mock import patch
from selenium.common.exceptions import NoSuchWindowException
import pytest


class Corona:

    @staticmethod
    def get_cookies():
        return '123'


@patch('QWeb.internal.browser.get_current_browser')
def test_delete_all_cookies(patched_browser):
    patched_browser.return_value = None
    with pytest.raises(NoSuchWindowException):
        cookies.delete_all_cookies()


@patch('QWeb.internal.browser.get_current_browser')
def test_get_cookies_fail(patched_browser):
    patched_browser.return_value = None
    with pytest.raises(NoSuchWindowException):
        cookies.get_cookies()
