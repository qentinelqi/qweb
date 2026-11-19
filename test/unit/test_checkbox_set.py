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
"""actions.checkbox_set when the checkbox input refuses the click.

The steps after a refused click: the locator element when there is one, else
the parent when it is a label, else the parent when the input is visually
hidden, and the ``.checked`` write only when the input is still in the wrong
state.
"""

from unittest.mock import MagicMock, patch

from selenium.common.exceptions import WebDriverException

from QWeb.internal import actions


def _checkbox(parent_tag="div", selected_after_clicks=False):
    """An input whose own click is refused, and its parent."""
    parent = MagicMock(name="parent")
    parent.tag_name = parent_tag
    box = MagicMock(name="input")
    box.click.side_effect = WebDriverException("element click intercepted")
    box.find_element.return_value = parent
    box.is_selected.return_value = selected_after_clicks
    return box, parent


def _set(box, locator=None, hidden=False, value=True):
    """Run checkbox_set; return the scripts it executed."""
    scripts = []
    run = patch.object(
        actions.javascript, "execute_javascript", side_effect=lambda s, *a: scripts.append(s)
    )
    with patch.object(actions.checkbox, "is_checked", return_value=not value):
        with patch.object(actions, "_is_visually_hidden", return_value=hidden), run:
            actions.checkbox_set(box, locator, value=value)
    return scripts


def test_nothing_is_clicked_when_the_state_is_already_right():
    box, parent = _checkbox()
    with patch.object(actions.checkbox, "is_checked", return_value=True):
        actions.checkbox_set(box, None, value=True)
    box.click.assert_not_called()
    parent.click.assert_not_called()


def test_the_wrapper_of_a_hidden_input_is_clicked_and_nothing_is_written():
    box, parent = _checkbox(selected_after_clicks=True)
    scripts = _set(box, hidden=True)
    parent.click.assert_called_once_with()
    assert scripts == []


def test_the_write_still_runs_when_the_wrapper_click_changes_nothing():
    box, parent = _checkbox(selected_after_clicks=False)
    scripts = _set(box, hidden=True)
    parent.click.assert_called_once_with()
    assert scripts == ["arguments[0].checked=true"]


def test_the_write_still_runs_when_the_wrapper_refuses_the_click():
    # Switching off: the input is still selected after the refused clicks.
    box, parent = _checkbox(selected_after_clicks=True)
    parent.click.side_effect = WebDriverException("element not interactable")
    scripts = _set(box, hidden=True, value=False)
    assert scripts == ["arguments[0].checked=false"]


def test_the_parent_of_a_visible_input_is_not_clicked():
    box, parent = _checkbox(selected_after_clicks=False)
    scripts = _set(box, hidden=False)
    parent.click.assert_not_called()
    assert scripts == ["arguments[0].checked=true"]


def test_a_label_parent_is_clicked_once():
    box, parent = _checkbox(parent_tag="label", selected_after_clicks=True)
    scripts = _set(box, hidden=True)
    parent.click.assert_called_once_with()
    assert scripts == []


def test_a_locator_element_takes_the_click_and_the_parent_is_left_alone():
    box, parent = _checkbox()
    locator = MagicMock(name="locator")
    scripts = _set(box, locator=locator, hidden=True)
    locator.click.assert_called_once_with()
    box.find_element.assert_not_called()
    parent.click.assert_not_called()
    assert scripts == []


def test_one_pixel_counts_as_hidden():
    box = MagicMock(name="input")
    with patch.object(actions.javascript, "execute_javascript", return_value=True) as run:
        assert actions._is_visually_hidden(box) is True
    script, element = run.call_args.args
    assert element is box
    assert "rect.width <= 1 || rect.height <= 1" in script
    for rule in ('display === "none"', 'visibility === "hidden"', 'opacity === "0"'):
        assert rule in script


def test_a_driver_error_means_not_hidden():
    with patch.object(
        actions.javascript, "execute_javascript", side_effect=WebDriverException("stale")
    ):
        assert actions._is_visually_hidden(MagicMock(name="input")) is False
