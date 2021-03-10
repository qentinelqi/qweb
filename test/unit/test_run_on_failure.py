# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------
import pytest
import QWeb as QWeb_
from unittest.mock import Mock
# pylint: disable=no-member


def test_run_once():
    qweb = QWeb_.QWeb()
    QWeb_.BuiltIn.run_keyword = Mock()
    with pytest.raises(AttributeError):
        qweb.click_text(u"Browser not open")
    QWeb_.BuiltIn.run_keyword.assert_called_once()


def test_correct_keyword():
    keyword_name = 'Verify Text'
    qweb = QWeb_.QWeb(keyword_name)
    QWeb_.BuiltIn.run_keyword = Mock()
    with pytest.raises(AttributeError):
        qweb.click_text(u"Browser not open")
    QWeb_.BuiltIn.run_keyword.assert_called_with(keyword_name)


def test_not_failed():
    def dummy_keyword():
        return True
    QWeb_.keywords.browser.dummy_keyword = dummy_keyword
    qweb = QWeb_.QWeb()
    QWeb_.BuiltIn.run_keyword = Mock()
    qweb.dummy_keyword()
    QWeb_.BuiltIn.run_keyword.assert_not_called()
