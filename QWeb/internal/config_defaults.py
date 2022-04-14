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
"""
Default values for configuration items.
parameter name - (parameter value, adapter function)

All accepted parameter names must be defined here as the config
module allows only modifying existing parameters.

Config module stores any given parameter value to existing parameter.
Given parameter is passed to adapter function, if defined, before storage. If value should be
stored as is, set adapter function to None.

Usage from test script:
SetConfig    ScreenshotType    all

Usage from code:
from QWeb.internal.config_defaults import CONFIG
val = CONFIG["ScreenshotType"]
"""
from __future__ import annotations
from typing import Any, Union

from QWeb.internal.search_strategy import SearchStrategies
from QWeb.internal import util
from QWeb.internal.config import Config

CONFIG_DEFAULTS: dict[str, Any] = {
    "ScreenshotType": ("screenshot", None),
    "LineBreak": ("\ue004", util.set_line_break),
    "ClearKey": (None, util.set_clear_key),
    "CssSelectors": (True, util.par2bool),
    "LogScreenshot": (True, util.par2bool),
    "SearchDirection": ("closest", SearchStrategies.search_direction_validation),
    "CheckInputValue": (False, util.par2bool),
    "DefaultTimeout": ("10s", SearchStrategies.default_timeout_validation),
    "XHRTimeout": ("30", SearchStrategies.xhr_timeout_validation),
    "DefaultDocument": (True, util.par2bool),
    "InputHandler": ("selenium", util.set_input_handler),
    "CaseInsensitive": (False, util.par2bool),
    "AllInputElements":
    (SearchStrategies.ALL_INPUT_ELEMENTS, SearchStrategies.all_input_elements_validation),
    "MatchingInputElement":
    (SearchStrategies.MATCHING_INPUT_ELEMENT, SearchStrategies.matching_input_element_validation),
    "ActiveAreaXpath":
    (SearchStrategies.ACTIVE_AREA_XPATH, SearchStrategies.active_area_xpath_validation),
    "TextMatch": (SearchStrategies.TEXT_MATCH, SearchStrategies.text_match_validation),
    "ContainingTextMatch": (SearchStrategies.CONTAINING_TEXT_MATCH_CASE_SENSITIVE,
                            SearchStrategies.containing_text_match_validation),
    "IsModalXpath": (SearchStrategies.IS_MODAL_XPATH, SearchStrategies.clear_xpath),
    "VerifyAppAccuracy": (0.9999, None),
    "OffsetCheck": (True, util.par2bool),
    "Visibility": (True, util.par2bool),
    "InViewport": (False, util.par2bool),
    "WindowSize": ((0, 0), util.set_window_size),
    "DoubleClick": (False, util.par2bool),
    "LimitTraverse": (True, util.par2bool),
    "PartialMatch": (True, util.par2bool),
    "SearchMode": ("draw", None),
    "MultipleAnchors": (False, util.par2bool),
    "WindowFind": (False, util.par2bool),
    "ClickToFocus": (False, util.par2bool),
    "Debug_Run": (False, False),
    "HandleAlerts": (True, util.par2bool),
    "BlindReturn": (False, util.par2bool),
    "Headless": (False, util.par2bool),
    "Delay": ('0s', SearchStrategies.default_timeout_validation),
    "RunBefore": (None, util.validate_run_before),
    "RetryInterval": ('5s', SearchStrategies.default_timeout_validation),
    "RetryError": (None, None),
    "StayInCurrentFrame": (False, util.par2bool),
    "FrameTimeout": ("10s", SearchStrategies.default_timeout_validation),
    "AllTextNodes": (False, util.par2bool),
    "OSScreenshots": (False, util.par2bool),
    "RetinaDisplay": (util.is_retina(), util.par2bool),
    "LogMatchedIcons": (False, util.par2bool),
    "ShadowDOM": (False, util.par2bool),
    "HighlightColor": ("blue", util.highlight_validation)
}

CONFIG: Config = Config(CONFIG_DEFAULTS)
RETRIES_AMOUNT: int = 3
SHORT_DELAY: Union[int, float] = 0.2
LONG_DELAY: Union[int, float] = 1
