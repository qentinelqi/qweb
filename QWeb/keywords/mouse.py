# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2025 -            Copado Inc.
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
"""Keywords for mouse interaction and coordinates.

Additional helper keywords to separate mouse down and mouse up actions.
"""

from __future__ import annotations

from typing import Optional, Union

from robot.api.deco import keyword
from selenium.webdriver.remote.webelement import WebElement

from QWeb.internal import actions, javascript
from QWeb.internal.exceptions import QWebElementNotFoundError
from QWeb.keywords import element


@keyword(tags=("Mouse", "Interaction"))
def mouse_down(
    locator: Union[WebElement, str],
    anchor: str = "1",
    element_type: Optional[str] = None,
    timeout: Union[int, float, str] = 0,
    **kwargs,
) -> None:
    r"""Holds down mouse button on the element. Mouse will be held down until MouseUp
    keyword is called.

    Keyword takes WebElement or locator as input. Given locator must follow the syntax
    defined in GetWebElement keyword.

    Examples
    --------
    Using xpaths like with ClickElement etc. kw:s without specified
    element_type. Index must be given if element is not unique:

    .. code-block:: robotframework

        MouseDown      click_me     id         tag=button   # attribute and tag
        Sleep          2s
        MouseUp        //*[@id\="click_me"]    id   # xpath


    MouseDown using element_type attribute to locate element.
    Text elements works as ClickText, VerifyText, GetText etc.:

    .. code-block:: robotframework

        MouseDown     Log In    type    element_type=text
        MouseDown     Contact   id      element_type=text  anchor=Qentinel
        MouseDown     Contact   class   parent=div

    Item, Input, Dropdown, Checkbox elements:

    .. code-block:: robotframework

        MouseDown          Log In    id              element_type=item
        MouseDown          Username  placeholder     element_type=input
        MouseDown          Country   value           element_type=dropdown
        MouseDown          Gender    checked         element_type=checkbox

    Any element using css selectors:

    .. code-block:: robotframework

        MouseDown          input[type=button]   value    element_type=css

    All flags are available for using (timeout, anchor, index, visibility, parent, child etc.).
    in same way as you are using those with Qwords like ClickText/Item, TypeText, Dropdown etc.

    Parameters
    ----------
    locator : str or WebElement
        Visible text, attribute value, Xpath expression or WebElement.
    anchor : int
        Used when element_type is defined. Default=1 (first match)
    element_type : string
        Define element type/preferred searching method
        (available types: text, input, checkbox, item, dropdown or css).
    timeout : int
        How long we wait element to appear. Default=10 sec
    kwargs :
        |  Accepted kwargs:
        |       Any available for picked searching method.
        |       See interacting with text, item, input etc. elements from
        |       documentation. When using xpath as locator **index** should be
        |       specified unless xpath matches to a single element.

    Returns
    -------
    None

    Related keywords
    ----------------
    \`GetWebElement\`, \`MouseUp\, \`MouseMove\`
    """
    kwargs.pop("all_frames", None)
    if isinstance(locator, WebElement):
        webelement = locator
    else:
        webelement = element.get_webelement(locator,
                                            anchor,
                                            element_type,
                                            timeout,
                                            all_frames=False,
                                            **kwargs)

    if not webelement:
        raise QWebElementNotFoundError(
            f"Could not find element {locator}"
        )
    # first one if multiple returned
    if isinstance(webelement, list):
        webelement = webelement[0]

    actions.mouse_down(webelement)


@keyword(tags=("Mouse", "Interaction"))
def mouse_up(
    locator: Union[WebElement, str],
    anchor: str = "1",
    element_type: Optional[str] = None,
    timeout: Union[int, float, str] = 0,
    **kwargs,
) -> None:
    r"""Releases mouse button held down with MouseDown keyword.

    Keyword takes WebElement or locator as input. Given locator must follow the syntax
    defined in GetWebElement keyword.

    Examples
    --------
    Using xpaths like with ClickElement etc. kw:s without specified
    element_type. Index must be given if element is not unique:

    .. code-block:: robotframework

        MouseDown      click_me     id         tag=button   # attribute and tag
        Sleep          2s
        MouseUp        //*[@id\="click_me"]    id   # xpath


    MouseUp using element_type attribute to locate element.
    Text elements works as ClickText, VerifyText, GetText etc.:

    .. code-block:: robotframework

        MouseUp     Log In    type    element_type=text
        MouseUp     Contact   id      element_type=text  anchor=Qentinel
        MouseUp     Contact   class   parent=div

    Item, Input, Dropdown, Checkbox elements:

    .. code-block:: robotframework

        MouseUp          Log In    id              element_type=item
        MouseUp          Username  placeholder     element_type=input
        MouseUp          Country   value           element_type=dropdown
        MouseUp          Gender    checked         element_type=checkbox

    Any element using css selectors:

    .. code-block:: robotframework

        MouseUp          input[type=button]   value    element_type=css

    All flags are available for using (timeout, anchor, index, visibility, parent, child etc.).
    in same way as you are using those with Qwords like ClickText/Item, TypeText, Dropdown etc.

    Parameters
    ----------
    locator : str or WebElement
        Visible text, attribute value, Xpath expression or WebElement.
    anchor : int
        Used when element_type is defined. Default=1 (first match)
    element_type : string
        Define element type/preferred searching method
        (available types: text, input, checkbox, item, dropdown or css).
    timeout : int
        How long we wait element to appear. Default=10 sec
    kwargs :
        |  Accepted kwargs:
        |       Any available for picked searching method.
        |       See interacting with text, item, input etc. elements from
        |       documentation. When using xpath as locator **index** should be
        |       specified unless xpath matches to a single element.

    Returns
    -------
    None

    Related keywords
    ----------------
    \`GetWebElement\`, \`MouseUp\, \`MouseMove\`
    """
    kwargs.pop("all_frames", None)
    if isinstance(locator, WebElement):
        webelement = locator
    else:
        webelement = element.get_webelement(locator,
                                            anchor,
                                            element_type,
                                            timeout,
                                            all_frames=False,
                                            **kwargs)

    if not webelement:
        raise QWebElementNotFoundError(
            f"Could not find element {locator}"
        )

    # first one if multiple returned
    if isinstance(webelement, list):
        webelement = webelement[0]

    actions.mouse_up(webelement)


@keyword(tags=("Mouse", "Interaction"))
def mouse_move(x: int, y: int) -> None:
    r"""Moves mouse to the given coordinates.

    Examples
    --------
    Moving mouse to the given coordinates:

    .. code-block:: robotframework

        MouseMove    100    200



    Moving mouse to multiple coordinates (gestures, drawing etc.):

    .. code-block:: robotframework

        MouseMove    0    0
        MouseMove    100    200
        MouseMove    400    500



    Parameters
    ----------
    x : int
        x coordinate of the point to move
    y : int
        y coordinate of the point to move

    Returns
    -------
    None

    Related keywords
    ----------------
    \`GetWebElement\`, \`MouseUp\, \`MouseMove\`
    """
    actions.mouse_move(int(x), int(y))


@keyword(tags=("Mouse", "Interaction"))
def click_coordinates(x: int, y: int) -> None:
    r"""Clicks on the given coordinates.

    Examples
    --------
    Using direct coordinates withtout knowing the element:

    .. code-block:: robotframework

        ClickCoordinates    100     200


    Getting coordinates from element and clicking on it:

    .. code-block:: robotframework

        ${element}=    GetWebElement    //*[@id\="click_me"]    id
        ${coords}=     Evaluate    $elem.location
        ClickCoordinates    ${coords.x}    ${coords.y}


    Parameters
    ----------
    x : int
        x coordinate of the point to click
    y : int
        y coordinate of the point to click

    Returns
    -------
    None

    Related keywords
    ----------------
    \`MouseUp\, \`MouseMove\`
    """
    javascript.execute_javascript(f"el = document.elementFromPoint({x}, {y}); el.click()")
