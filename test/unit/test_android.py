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

from QWeb.internal.browser.android import open_browser
from unittest.mock import patch
import pytest


@patch('QWeb.internal.browser.android.webdriver.Remote')
@patch('QWeb.internal.browser.android.subprocess.check_output')
def test_android_open_browser(patch_subprocess, patch_webdriver):
    patch_subprocess.side_effect = [b'List of devices attached ad061603092984da09 device',
                                    b'6.0.1']
    patch_webdriver.return_value = '123'
    assert open_browser() == '123'


@patch('QWeb.internal.browser.android.subprocess.check_output')
def test_android_open_browser_raise_value_error(patch_subprocess):
    patch_subprocess.side_effect = [b'List of devices attached ad061603092984da09 device \
                                    emulator-5554 device',
                                    b'6.0.1']
    with pytest.raises(ValueError):
        open_browser()
