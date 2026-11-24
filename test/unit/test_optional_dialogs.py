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
"""QWeb must stay usable when tkinter (and thus robot Dialogs) is missing."""

import subprocess
import sys
import textwrap
from unittest.mock import Mock

import pytest
import QWeb as QWeb_
# pylint: disable=no-member


def test_import_without_tkinter():
    # Run in a fresh interpreter so the import failure does not leak into
    # other tests. Setting sys.modules entries to None makes imports raise
    # ModuleNotFoundError, just like on a Python build without tkinter.
    code = textwrap.dedent(
        """
        import sys
        for name in ("tkinter", "_tkinter", "robot.libraries.Dialogs"):
            sys.modules[name] = None
        import QWeb
        assert QWeb.Dialogs is None
        QWeb.QWeb()
        print("OK")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_dev_mode_without_dialogs_warns_and_reraises(monkeypatch):
    def failing_keyword():
        raise ValueError("boom")

    monkeypatch.setattr(QWeb_.keywords.browser, "failing_keyword", failing_keyword,
                        raising=False)
    monkeypatch.setattr(QWeb_, "Dialogs", None)
    monkeypatch.setattr(QWeb_.util, "get_rfw_variable_value", lambda *_a, **_k: True)
    monkeypatch.setattr(QWeb_.screenshot, "log_screenshot", Mock())
    warn = Mock()
    monkeypatch.setattr(QWeb_.logger, "warn", warn)
    debug_on = Mock()
    monkeypatch.setattr(QWeb_.debug, "debug_on", debug_on)

    qweb = QWeb_.QWeb()
    with pytest.raises(ValueError, match="boom"):
        qweb.failing_keyword()

    warn.assert_called_once()
    assert "tkinter" in warn.call_args[0][0]
    debug_on.assert_not_called()
