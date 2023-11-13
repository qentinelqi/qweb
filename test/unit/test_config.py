# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2019 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------
import pytest

from QWeb.internal.config_defaults import CONFIG
from QWeb.keywords import config
from QWeb import custom_config
from QWeb.internal.search_strategy import SearchStrategies
from QWeb.internal import util


class TestConfig:

    @staticmethod
    def setup():
        """ Use test specific configs. """
        pass  # pylint: disable=unnecessary-pass

    @staticmethod
    def teardown():
        """ Return original configs. """
        config.reset_config()

    @staticmethod
    def test_get_config():
        assert config.get_config("ScreenshotType") == "screenshot"
        assert config.get_config("DefaultDocument") is True
        assert config.get_config("MatchingInputElement") == SearchStrategies.MATCHING_INPUT_ELEMENT
        assert config.get_config("CssSelectors") is True
        assert config.get_config("TextMatch") == SearchStrategies.TEXT_MATCH
        assert config.get_config("HighlightColor") == "blue"

    @staticmethod
    def test_get_config_with_brackets():
        assert CONFIG["ScreenshotType"] == "screenshot"
        assert CONFIG["DefaultDocument"] is True
        assert CONFIG["MatchingInputElement"] == SearchStrategies.MATCHING_INPUT_ELEMENT
        assert CONFIG["CssSelectors"] is True
        assert CONFIG["TextMatch"] == SearchStrategies.TEXT_MATCH
        assert CONFIG["HighlightColor"] == "blue"

    @staticmethod
    def test_set_config():
        old_val = config.set_config("ScreenshotType", "full_screen")
        assert old_val == "screenshot"
        assert config.get_config("ScreenshotType") == "full_screen"
        assert CONFIG["ScreenshotType"] == "full_screen"

        old_val = config.set_config("DefaultDocument", False)
        assert old_val is True
        assert config.get_config("DefaultDocument") is False
        assert CONFIG["DefaultDocument"] is False

        old_val = config.set_config("RunBefore", "text.verify_no_text('Loading')")
        assert old_val == None
        new_kw = ["VerifyText", "Test", "timeout=10"]
        old_val = config.set_config("RunBefore", new_kw)
        assert old_val == "text.verify_no_text('Loading')"
        new_kw = "Verify Something"
        old_val = config.set_config("RunBefore", new_kw)
        assert old_val == ["VerifyText", "Test", "timeout=10"]
        assert CONFIG["RunBefore"] == "Verify Something"
        config.reset_config("RunBefore")
        assert CONFIG["RunBefore"] == None

        old_val = config.set_config("ShadowDOM", True)
        assert old_val is False
        assert config.get_config("ShadowDOM") is True
        assert CONFIG["ShadowDOM"] is True

        old_val = config.set_config("HighlightColor", "orange")
        assert old_val == "blue"
        assert config.get_config("HighlightColor") == "orange"
        assert CONFIG["HighlightColor"] == "orange"

    @staticmethod
    def test_reset_config():
        old_val = config.set_config("ScreenshotType", "full_screen")
        assert old_val == "screenshot"
        resetted_val = config.reset_config("ScreenshotType")
        assert resetted_val == "screenshot"

        old_val = config.set_config("DefaultDocument", False)
        assert old_val is True
        resetted_val = config.reset_config("DefaultDocument")
        assert resetted_val is True

        old_val = config.set_config("ScreenshotType", "full_screen")
        assert old_val == "screenshot"
        old_val = config.set_config("DefaultDocument", False)
        assert old_val is True

        old_val = config.set_config("CaseInsensitive", True)
        assert old_val is False
        assert config.get_config("CaseInsensitive") is True
        # should automatically change ContainingTextMatch
        assert config.get_config("ContainingTextMatch") == SearchStrategies.CONTAINING_TEXT_MATCH_CASE_INSENSITIVE 
        resetted_val = config.reset_config("CaseInsensitive")
        assert resetted_val is False
        assert config.get_config("ContainingTextMatch") == SearchStrategies.CONTAINING_TEXT_MATCH_CASE_SENSITIVE

        old_val = config.set_config("HighlightColor", "purple")
        assert old_val == "blue"
        assert config.get_config("HighlightColor") == "purple"
        resetted_val = config.reset_config("HighlightColor")
        assert resetted_val == "blue"

        old_val = config.set_config("ShadowDOM", True)
        assert old_val is False
        assert config.get_config("ShadowDOM") is True

        config.reset_config()
        assert config.get_config("ScreenshotType") == "screenshot"
        assert config.get_config("DefaultDocument") is True
        assert config.get_config("HighlightColor") == "blue"
        assert config.get_config("ShadowDOM") is False

    @staticmethod
    def test_non_existing_parameter():
        with pytest.raises(ValueError):
            config.get_config("new")

        with pytest.raises(ValueError):
            config.set_config("new", 100)

    @staticmethod
    def test_non_accepted_color():
        with pytest.raises(ValueError):
            config.set_config("HighlightColor", "salmon pink")
        assert config.get_config("HighlightColor") == "blue"

    @staticmethod
    def test_pixel_parser_case_one():
        # pylint: disable=W0212
        window_size = util._parse_pixels('1920x1080')
        assert window_size == ('1920', '1080')

    @staticmethod
    def test_pixel_parser_case_two():
        # pylint: disable=W0212
        window_size = util._parse_pixels('1920X1080')
        assert window_size == ('1920', '1080')

    @staticmethod
    def test_pixel_parser_case_three():
        # pylint: disable=W0212
        with pytest.raises(ValueError):
            util._parse_pixels('1920, 1080')

    @staticmethod
    def test_set_non_callable_wait_function():        
        # pylint: disable=W0212
        with pytest.raises(ValueError):
            custom_config.set_wait_function("not a funcS")

    @staticmethod
    def test_set_callable_wait_function():
        def my_wait_function():
            return None
        
        custom_config.set_wait_function(my_wait_function)
