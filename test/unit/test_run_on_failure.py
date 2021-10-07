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
