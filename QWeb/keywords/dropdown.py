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
"""Keywords for dropdown elements.

Dropdown elements are considered to be any <select> tagged element.
"""
from __future__ import annotations
from typing import Union

from robot.api.deco import keyword
from QWeb.internal import decorators, actions
from QWeb.internal.dropdown import get_dd_elements_from_all_documents as _get_dd_elements


@keyword(tags=("Dropdown", "Interaction"))
@decorators.timeout_decorator
def drop_down(locator: str,
              option: str,
              anchor: str = '1',
              timeout: Union[int, float, str] = 0,
              index: int = 1,
              unselect: bool = False,
              **kwargs) -> None:
    r"""Select an option from dropdown menu/list.

    Examples
    --------
    .. code-block:: robotframework

        DropDown        Canis   Collie

    In the above example the DropDown keyword will select from a dropdown
    the option: Collie.

    How the dropdown element is searched:
    The dropdown element is first attempted to be matched based on its
    label text and then options.
    If you give one of the dropdown's options as locator, the element
    will be matched in this search pass.

    If there are multiple instances of a dropdown with text Canis on the page, first one
    will be clicked unless 'anchor' is given. You can
    specific which one should be clicked by either:

    - a number or
    - a word that is near to the word Canis

    For example

    .. code-block:: robotframework

        DropDown    Canis    Collie   anchor=3     # Uses third Canis dropdown
        DropDown    Canis    Collie   anchor=dog   # Uses Canis dropdown near the word text dog

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        Dropdown    r1c1          Qentinel
        Dropdown    r-1c3         Robot     #last row, third cell
        Dropdown    r?Robot/c-1   Qentinel  #row that contains text Robot, last cell

    Choose dropdown option with index:

    .. code-block:: robotframework

        Dropdown    Canis       [[2]]

    Unselect a selected option from multiselection dropdown:

    .. code-block:: robotframework

        Dropdown    Canis       Collie  unselect=True

    Parameters
    ----------
    locator : str
        Locator for searching the dropdown element
    option : str
        Label of the option you want to select
    anchor : str
        Optional parameter for locating the element if locator text is not unique
    timeout : str | int
        How long we search before failing. Default = Search Strategy default timeout (10s)
    index : int
        If cell contains more than one dropdown elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    QWebElementNotFoundErr
        Dropdown element not found

    Related keywords
    ----------------
    \`GetDropDownValues\`, \`GetSelected\`, \`VerifyOption\`,
    \`VerifyNoOption\`, \`VerifySelectedOption\`
    """
    select = _get_dd_elements(locator, anchor, index=index, **kwargs)
    if actions.select_option(select, option, timeout=timeout, unselect=unselect):
        return


@keyword(tags=("Dropdown", "Verification"))
@decorators.timeout_decorator
def verify_selected_option(locator: str,
                           expected_option: str,
                           anchor: str = '1',
                           timeout: Union[int, float, str] = 0,
                           index: int = 1,
                           **kwargs) -> None:
    r"""Verify that an option is selected from dropdown menu/list.
    Note: with multiselection dropdown verify each option individually.

    Examples
    --------
    .. code-block:: robotframework

        VerifySelectedOption    Canis   Collie

    In the above example the VerifySelectedOption keyword verifies from a dropdown
    that Collie is selected.

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        VerifySelectedOption    r1c1          Qentinel
        VerifySelectedOption    r-1c3         Robot     #last row, third cell
        VerifySelectedOption    r?Robot/c-1   Qentinel  #row that contains text Robot, last cell

    Parameters
    ----------
    locator : str
        Locator for searching the dropdown element. Usually some label-text
    expected_option : str
        option which should be selected
    anchor : str
        Optional parameter for locating the element if locator text is not unique
    timeout: str
         How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one dropdown elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Related keywords
    ----------------
    \`DropDown\`, \`GetDropDownValues\`, \`GetSelected\`, \`VerifyOption\`, \`VerifyNoOption\`
    """
    select = _get_dd_elements(locator, anchor=anchor, index=index, **kwargs)
    if actions.get_selected_value(select, expected_option, timeout=timeout):
        return


@keyword(tags=("Dropdown", "Getters"))
@decorators.timeout_decorator
def get_selected(locator: str,
                 anchor: str = '1',
                 timeout: Union[int, float, str] = 0,
                 index: int = 1,
                 **kwargs) -> None:
    r"""Get selected option to variable from dropdown menu/list.

    Examples
    --------
    .. code-block:: robotframework

        ${VALUE}    GetSelected    Canis

    In the above example we get selected value from dropdown Canis.

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        ${VALUE}    GetSelected    r1c1
        ${VALUE}    GetSelected    r-1c3             #last row, third cell
        ${VALUE}    GetSelected    r?Robot/c-1      #row that contains text Robot, last cell

    Parameters
    ----------
    locator : unicode
        Locator for searching the dropdown element. Usually some label-text
    anchor : unicode
        Optional parameter for locating the element if locator text is not unique
    timeout: unicode
         How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one dropdown elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Returns
    -------
    selected: str
        With multiselection dropdowns returns a string containing all values
        separated by comma (",")

    Related keywords
    ----------------
    \`DropDown\`, \`GetDropDownValues\`, \`VerifyOption\`,
    \`VerifyNoOption\`, \`VerifySelectedOption\`
    """
    select = _get_dd_elements(locator, anchor=anchor, index=index, **kwargs)
    return actions.get_selected_value(select, timeout=timeout)


@keyword(tags=("Dropdown", "Verification"))
@decorators.timeout_decorator
def verify_option(locator: str,
                  expected_option: str,
                  anchor: str = '1',
                  timeout: Union[int, float, str] = 0,
                  index: int = 1,
                  **kwargs) -> None:
    r"""Verify that option exist in dropdown menu/list.

    Examples
    --------
    .. code-block:: robotframework

       VerifyOption    Canis   Collie

    In the above example the VerifyOption keyword verifies from a dropdown
    that Collie is in a list.

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

       VerifySelectedOption    r1c1          Qentinel

    Parameters
    ----------
    locator : str
        Locator for searching the dropdown element. Usually some label-text
    expected_option : str
        option that should be included in dropdown options
    anchor : str
        Optional parameter for locating the element if locator text is not unique
    timeout: str
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one dropdown elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Related keywords
    ----------------
    \`DropDown\`, \`GetDropDownValues\`, \`GetSelected\`,
    \`VerifyNoOption\`, \`VerifySelectedOption\`
    """
    select = _get_dd_elements(locator, anchor=anchor, index=index, **kwargs)
    if actions.get_select_options(select, expected_option, timeout=timeout):
        return


@keyword(tags=("Dropdown", "Getters"))
@decorators.timeout_decorator
def get_drop_down_values(locator: str,
                         anchor: str = '1',
                         timeout: Union[int, float, str] = 0,
                         index: int = 1,
                         **kwargs) -> None:
    r"""Return all options from a dropdown menu/list.

    Examples
    --------
    .. code-block:: robotframework

        ${all_options}=     GetDropDownValues     Canis     Collie
        log     ${all_options}

    In the above example the GetDropDownValues keyword saves all items from the
    dropdown menu Canis to a variable.

    This keyword can also be used with table cells and XPaths. When using XPaths, the equal sign "="
    must be escaped with a "\\".

    Parameters
    ----------
    locator : str
        Locator for searching the dropdown element. Usually some label-text
    anchor : str
        Optional parameter for locating the element if locator text is not unique
    timeout: str
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one dropdown elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Related keywords
    ----------------
    \`DropDown\`, \`GetSelected\`, \`VerifyOption\`, \`VerifyNoOption\`, \`VerifySelectedOption\`
    """
    select = _get_dd_elements(locator, anchor, index=index, **kwargs)
    return actions.get_select_options(select, timeout=timeout)


@keyword(tags=("Dropdown", "Verification"))
@decorators.timeout_decorator
def verify_no_option(locator: str,
                     option: str,
                     anchor: str = '1',
                     timeout: Union[int, float, str] = 0,
                     index: int = 1,
                     **kwargs) -> None:
    r"""Verify that a given option is not in a dropdown menu/list.

    Examples
    --------
    .. code-block:: robotframework

        VerifyNoOption     Foobar    Cat

    In the above example VerifyNoOption keyword checks that the option "Cat" is not found
    from the Foobar dropdown menu/list.

    This keyword can also be used with table cells and XPaths. When using XPaths, the equal sign "="
    must be escaped with a "\\".

    Parameters
    ----------
    locator : str
        Locator for searching the dropdown element. Usually some label-text
    option : str
        Option text that should not exists in options list
    anchor : str
        Optional parameter for locating the element if locator text is not unique
    timeout: str
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If cell contains more than one dropdown elements index is needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Related keywords
    ----------------
    \`DropDown\`, \`GetDropDownValues\`, \`GetSelected\`, \`VerifyOption\`, \`VerifySelectedOption\`
    """
    select = _get_dd_elements(locator, anchor, index=index, **kwargs)
    if actions.is_not_in_dropdown(select, option, timeout=timeout):
        return
