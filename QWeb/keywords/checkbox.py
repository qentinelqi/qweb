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
"""Keywords for checkbox elements.

Checkboxes are those that can be checked/selected and unchecked/unselected.
"""
from __future__ import annotations
from typing import Union

from robot.api.deco import keyword
from QWeb.internal import checkbox, actions, decorators
import QWeb.internal.element
from QWeb.internal.exceptions import QWebValueError


@keyword(tags=("Checkbox", "Interaction"))
@decorators.timeout_decorator
def click_checkbox(locator: str,
                   value: str,
                   anchor: str = "1",
                   timeout: Union[int, float, str] = 0,
                   index: int = 1,
                   **kwargs) -> None:
    r"""Check or uncheck a checkbox.

    Examples
    --------
    .. code-block:: robotframework

        ClickCheckbox    I am not a robot    on
        ClickCheckbox    I am not a robot    off

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        ClickCheckbox    r1c1               on
        ClickCheckbox    r-1c3              off  #last row, third cell
        ClickCheckbox    r?Robot/c-1        on   #row that contains text Robot, last cell

    With anchor

    .. code-block:: robotframework

        ClickCheckbox    I am not a robot    on    anchor text
        ClickCheckbox    r?Robot/c-1         on    Test  #row contains texts Robot and Test
        ClickCheckbox    r?Robot/c-1         on    3    #third row which contains text Robot

    Parameters
    ----------
    locator : str
        Text that locates the checkbox. The checkbox that is closest to the
        text is selected. Also one can use xpath by adding xpath= prefix and
        then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
    value : str
        Value of the checkbox. On or off.
    anchor : str (default None)
        Text near the checkbox's locator element. If the page contains many
        places where the locator text is then anchor is used to get the
        one that is closest to it.
    timeout : str | int
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one checkbox elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    QWebElementNotFoundErr
        CheckBox element not found

    Related keywords
    ----------------
    \`VerifyCheckbox\`, \`VerifyCheckboxStatus\`, \`VerifyCheckboxValue\`
    """
    checkbox_element, locator_element = checkbox.get_checkbox_elements_from_all_documents(
        locator, anchor=anchor, index=index, **kwargs)
    if checkbox_element:
        if value.lower() == "on":
            actions.checkbox_set(checkbox_element, locator_element, value=True, timeout=timeout)
        else:
            actions.checkbox_set(checkbox_element, locator_element, value=False, timeout=timeout)


@keyword(tags=("Checkbox", "Verification"))
@decorators.timeout_decorator
def verify_checkbox_status(
        locator: str,
        status: str,
        anchor: str = "1",
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        index=1,
        **kwargs) -> None:
    r"""Verify checkbox is enabled or disabled.

    In other words verify can user interact with a checkbox or not.

    Examples
    --------
    .. code-block:: robotframework

        VerifyCheckboxStatus    checked    enabled

     With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        VerifyCheckboxStatus    r1c1        disabled
        VerifyCheckboxStatus    r-1c-1      enabled  #last row, last cell
        VerifyCheckboxStatus    r?Robot/c3  enabled  #row that contains text Robot, cell c3

    With anchor

    .. code-block:: robotframework

        VerifyCheckboxStatus   Checked    disabled     anchor text

    Parameters
    ----------
    locator : str
        Text that locates the checkbox. The checkbox that is closest to the
        text is selected. Also one can use xpath by adding xpath= prefix and
        then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
    status : str
        Status for the checkbox. Either enabled or disabled.
    anchor : str (default None)
        Text near the checkbox's locator element. If the page contains many
        places where the locator text is then anchor is used to get the
        one that is closest to it.
    timeout : str | int
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one checkbox elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    ValueError
        Checkbox interaction with the checkbox was not the same

    Related keywords
    ----------------
    \`ClickCheckbox\`, \`VerifyCheckbox\`, \`VerifyCheckboxValue\`
    """
    checkbox_element, _ = checkbox.get_checkbox_elements_from_all_documents(locator,
                                                                            anchor=anchor,
                                                                            index=index,
                                                                            **kwargs)
    status = status.lower()
    if status.lower() == "enabled":
        if not QWeb.internal.element.is_enabled(checkbox_element):
            raise QWebValueError('The checkbox was disabled')
    elif status.lower() == "disabled":
        if QWeb.internal.element.is_enabled(checkbox_element):
            raise QWebValueError('The checkbox was enabled')
    else:
        raise QWebValueError('Unkown status: "{}"'.format(status))


@keyword(tags=("Checkbox", "Verification"))
@decorators.timeout_decorator
def verify_checkbox_value(
        locator: str,
        value: str,
        anchor: str = "1",
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        index: int = 1,
        **kwargs) -> None:
    r"""Verify checkbox is on (checked) or off (unchecked).

    Examples
    --------
    .. code-block:: robotframework

        VerifyCheckboxValue    Mercedes           on

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        VerifyCheckboxValue    r1c1        on
        VerifyCheckboxValue    r-1c-1      on  #last row, last cell
        VerifyCheckboxValue    r?Robot/c3  on   #row that contains text Robot, cell c3

    With anchor

    .. code-block:: robotframework

        VerifyCheckboxValue    Mercedes          off     Car
        VerifyCheckboxValue    r?Robot/c3   on   2  #second row that contains text Robot

    Parameters
    ----------
    locator : str
        Text that locates the checkbox. The checkbox that is closest to the
        text is selected. Also one can use xpath by adding xpath= prefix and
        then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
    value : str
        Value of the checkbox. On or off.
    anchor : str (default None)
        Text near the checkbox's locator element. If the page contains many
        places where the locator text is then anchor is used to get the
        one that is closest to it.
    timeout : str | int
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one checkbox elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    ValueError : The checkbox value is not the same

    Related keywords
    ----------------
    \`ClickCheckbox\`, \`VerifyCheckbox\`, \`VerifyCheckboxStatus\`
    """
    checkbox_element, _ = checkbox.get_checkbox_elements_from_all_documents(locator,
                                                                            anchor=anchor,
                                                                            index=index,
                                                                            **kwargs)
    value = value.lower()
    if value.lower() == "on":
        if not checkbox.is_checked(checkbox_element):
            raise QWebValueError('The checkbox was not checked.')
    elif value.lower() == "off":
        if checkbox.is_checked(checkbox_element):
            raise QWebValueError('The checkbox was checked')
    else:
        raise QWebValueError('Unkown value: "{}"'.format(value))


@keyword(tags=("Checkbox", "Verification"))
@decorators.timeout_decorator
def verify_checkbox(
        locator: str,
        anchor: str = '1',
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        index: int = 1,
        **kwargs) -> None:
    r"""Verify that checkbox element exist.

    Examples
    --------
    .. code-block:: robotframework

        VerifyCheckbox    Mercedes
        VerifyCheckbox    r1c1

    With anchor

    .. code-block:: robotframework

        VerifyCheckbox    Mercedes      Cars
        VerifyCheckbox    r?Foo/c2      Bar  #row contain texts Foo and Bar

    Parameters
    ----------
    locator : str
        Text that locates the checkbox. The checkbox that is closest to the
        text is selected. Also one can use xpath by adding xpath= prefix and
        then the xpath. Error is raised if the xpath matches to multiple
        elements.
    anchor : str (default None)
        Text near the checkbox's locator element. If the page contains many
        places where the locator text is then anchor is used to get the
        one that is closest to it.
    timeout : str | int
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one checkbox elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    NoSuchElementException: Checkbox element not found

    Related keywords
    ----------------
    \`ClickCheckbox\`, \`VerifyCheckboxStatus\`, \`VerifyCheckboxValue\`
    """
    checkbox_element, _ = checkbox.get_checkbox_elements_from_all_documents(locator,
                                                                            anchor=anchor,
                                                                            index=index,
                                                                            **kwargs)
    if checkbox_element:
        return
