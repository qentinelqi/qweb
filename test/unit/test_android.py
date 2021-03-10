# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
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
