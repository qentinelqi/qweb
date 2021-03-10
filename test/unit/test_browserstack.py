# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------

from QWeb.internal.browser.bs_desktop import open_browser as ob_desktop
from QWeb.internal.browser.bs_mobile import open_browser as ob_mobile
from unittest.mock import patch
from QWeb.internal.exceptions import QWebException
import pytest


@patch('QWeb.internal.browser.bs_desktop.BuiltIn.get_variable_value')
def test_desktop_bs_open_browser(patch_robot_builtin):
    patch_robot_builtin.return_value = 'foobar'
    with pytest.raises(QWebException):
        ob_desktop('asd', 'project_name', 'run_id_test')


@patch('QWeb.internal.browser.bs_mobile.BuiltIn.get_variable_value')
def test_mobile_bs_open_browser(patch_robot_builtin):
    patch_robot_builtin.return_value = 'foobar'
    with pytest.raises(QWebException):
        ob_mobile('asd', 'project_name', 'run_id_test')
