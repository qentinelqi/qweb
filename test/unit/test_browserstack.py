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
