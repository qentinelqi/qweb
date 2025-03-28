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
"""Keywords for general elements that are retrieved using XPaths."""

from __future__ import annotations
from typing import Union, Optional, Dict
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from robot.api.deco import keyword
from QWeb.internal.exceptions import QWebValueError, QWebElementNotFoundError
from QWeb.internal import element, decorators, actions, text, input_, dropdown, checkbox
from QWeb.internal.config_defaults import CONFIG


@keyword(tags=["Interaction"])
@decorators.timeout_decorator
def click_element(
    xpath: Union[WebElement, str],
    timeout: Union[int, float, str] = 0,
    js: bool = False,
    index: int = 1,
    **kwargs,
) -> None:
    r"""Click element specified by xpath.

    Examples
    --------
    .. code-block:: robotframework

        ClickElement          click_me      tag=button
        ClickElement          //*[@id\="click_me"]
        ClickElement          xpath\=//*[@id\="click_me"]
        # using WebElement instance
        ${elem}=              GetWebElement    Click Me    element_type=text
        ClickElement          ${elem}

    To double-click element, use argument **doubleclick=True**

    .. code-block:: robotframework

        ClickText             double_click_me       doubleclick=True

    Or use SetConfig

    .. code-block:: robotframework

        SetConfig             DoubleClick           On
        ClickElement          double_click_me       tag=button

    Parameters
    ----------
    xpath : str | selenium.webdriver.remote.webelement.WebElement
        Xpath expression with or without xpath= prefix. The equal sign "=" must be escaped
        with a "\\".
        Can also be a WebElement instance returned by GetWebElement keyword or javascript.
    timeout : int
        How long we wait before failing.
    js : boolean
        If set to true, uses javascript click instead of Selenium.
    index : int
        If multiple found, use index to pick correct one.
    kwargs :
        |  Accepted kwargs:
        |       tag : html tag of preferred elemenr -
        |           If tag is used then element is found
        |           by some of it's attribute (xpath is not needed)
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Related keywords
    ----------------
    \`ClickCell\`, \`ClickCheckbox\`, \`ClickIcon\`, \`ClickItem\`, \`ClickList\`,
    \`ClickText\`, \`ClickUntil\`, \`ClickWhile\`, \`RightClick\`, \`VerifyElement\`
    """
    if isinstance(xpath, WebElement):
        web_element = xpath
    else:
        index = int(index) - 1
        kwargs["element_kw"] = True
        if "tag" in kwargs:
            web_element = element.get_elements_by_attributes(kwargs.get("tag"), xpath, **kwargs)[
                index
            ]
        else:
            web_element = element.get_unique_element_by_xpath(xpath, index=index)
    if actions.execute_click_and_verify_condition(web_element, timeout=timeout, js=js, **kwargs):
        return


@keyword(tags=["Interaction"])
@decorators.timeout_decorator
def right_click(
    xpath: str,
    timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
    index: int = 1,
    **kwargs,
) -> None:
    r"""Right clicks the element.

    Examples
    --------
    .. code-block:: robotframework

        RightClick          click_me      tag=button
        RightClick          //*[@id\="click_me"]
        RightClick          xpath\=//*[@id\="click_me"]

    Parameters
    ----------
    xpath : str
        Xpath expression with or without xpath= prefix. The equal sign "=" must be escaped
        with a "\\".
    timeout : int
        How long we wait before failing.
    index : int
        If multiple found, use index to pick correct one.
    kwargs :
        |  Accepted kwargs:
        |       tag : html tag of preferred element -
        |           If tag is used then element is found
        |           by some of it's attribute (xpath is not needed)
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Related keywords
    ----------------
    \`ClickElement\`, \`ClickItem\`, \`ClickText\`
    """
    index = int(index) - 1
    kwargs["element_kw"] = True
    if "tag" in kwargs:
        web_element = element.get_elements_by_attributes(kwargs.get("tag"), xpath, **kwargs)[index]
    else:
        web_element = element.get_unique_element_by_xpath(xpath, index=index)
    actions.right_click(web_element)


@keyword(tags=["Interaction"])
@decorators.timeout_decorator
def hover_element(
    xpath: Union[WebElement, str],
    timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
    index: int = 1,
    **kwargs,
) -> None:
    r"""Hover the element specified by the xpath selector.

    Examples
    --------
    .. code-block:: robotframework

        HoverElement          //*[@id\="hover_me"]
        HoverElement          xpath\=//*[@id="hover_me"]

    Parameters
    ----------
    xpath : str | selenium.webdriver.remote.webelement.WebElement
        Xpath expression with or without xpath= prefix. The equal sign "=" must be escaped
        with a "\\".
        Can also be a WebElement instance returned by GetWebElement keyword or javascript.
    timeout : int
        How long we wait before failing.
    index : int
        If multiple found, use index to pick correct one.
    kwargs :
        |  Accepted kwargs:
        |       tag : html tag of preferred element -
        |           If tag is used then element is found
        |           by some of it's attribute (xpath is not needed)
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Related keywords
    ----------------
    \`HoverItem\`, \`HoverText\`, \`HoverTo\`, \`Scroll\`,
    \`ScrollText\`, \`ScrollTo\`
    """
    if isinstance(xpath, WebElement):
        web_element = xpath
    else:
        index = int(index) - 1
        kwargs["element_kw"] = True
        if "tag" in kwargs:
            web_element = element.get_elements_by_attributes(kwargs.get("tag"), xpath, **kwargs)[
                index
            ]
        else:
            web_element = element.get_unique_element_by_xpath(xpath, index=index)

    actions.hover_to(web_element, timeout=timeout)


@keyword(tags=["Getters"])
@decorators.timeout_decorator
def get_element_count(
    locator: str,
    timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
    **kwargs,
) -> int:
    r"""Get count of appearances for certain web element.

    Keyword waits until timeout has passed. If timeout is not specified, it
    uses default timeout that can be adjusted with DefaultTimeout keyword.

    GetElementCount does not require for the text to be unique.

    Examples
    --------
    .. code-block:: robotframework

        ${COUNT}    GetElementCount       //*[@id\="Foo"]
        ${COUNT}    GetElementCount       Foo    tag=div

    Parameters
    ----------
    locator : str
        Xpath or some attribute value of element. When using XPaths, the equal sign "=" must be
        escaped with a "\\".
    timeout : str | int
        How long we try to find text before failing. Default 10 (seconds)
    Accepted kwargs:
        tag=tagname: Needed when attribute value is used as a locator

    Related keywords
    ----------------
    \`GetTextCount\`, \`GetWebElement\`
    """
    kwargs["element_kw"] = True
    if "tag" in kwargs:
        web_elements = element.get_elements_by_attributes(kwargs.get("tag"), locator, **kwargs)
    else:
        web_elements = element.get_webelements(locator, **kwargs)
    if web_elements:
        return len(web_elements)
    raise QWebElementNotFoundError("Webelements not found")


@keyword(tags=["Verification"])
def is_element(
    xpath: str,
    timeout: Union[int, float, str] = "0.1s",
    index: int = 1,  # pylint: disable=unused-argument
    **kwargs,
) -> bool:
    r"""Return True if element is visible.

    Examples
    --------
    .. code-block:: robotframework

        $note_visible=  IsElement        Paused
        $note_visible=  IsElement        Paused     5s

    Parameters
    ----------
    xpath : str
        Xpath to be searched from the screen.

    timeout : str | int
        How long we wait for text to appear before returning. Default 0.1s
    index : int
        If multiple found, use index to pick correct one.
    kwargs :
        |  Accepted kwargs:
        |       tag : html tag of preferred elemenr -
        |           If tag is used then element is found
        |           by some of it's attribute (xpath is not needed)
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Returns
    -------
    Bool : True or False

    Related keywords
    ----------------
    \`ClickElement\`, \`GetAttribute\`, \`GetWebElement\`, \`GetElementCount\`,
    \`IsAlert\`, \`IsIcon\`, \`IsText\`, \`VerifyElement\`
    """
    try:
        verify_element(xpath, timeout, **kwargs)
        return True
    except QWebElementNotFoundError:
        return False


@keyword(tags=["Verification"])
@decorators.timeout_decorator
def verify_element(xpath: str, timeout: Union[int, float, str] = 0, **kwargs) -> None:  # pylint: disable=unused-argument
    r"""Verify that element can be found on the page and it is visible.

    Examples
    --------
    .. code-block:: robotframework

       VerifyElement          //*[@id\="wait_me"]

    This keyword has timeout functionality. If the element is not visible after
    given timeout, error is raised.
    For example.

    .. code-block:: robotframework

        VerifyElement          //*[@id\="wait_me"]       20   #waits 20 seconds

    Parameters
    ----------
    xpath : str
        Xpath expression without xpath= prefix. The equal sign "=" must be escaped with a "\\".
    timeout : str | int
        Timeout for finding the element. If the element is not visible after
        given timeout, error is raised. The str is converted to integer
        using robot.utils.timestr_to_secs. (default 10 seconds)
    kwargs :
        |  Accepted kwargs:
        |       tag : html tag of preferred elemenr -
        |           If tag is used then element is found
        |           by some of it's attribute (xpath is not needed)
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    QWebElementNotFoundError
        Page did not contain element

    Related keywords
    ----------------
    \`ClickElement\`, \`GetAttribute\`, \`GetWebElement\`, \`GetElementCount\`,
    \`VerifyItem\`, \`VerifyText\`
    """
    kwargs["element_kw"] = True
    if "tag" in kwargs:
        web_elements = element.get_visible_elements_from_elements(
            element.get_elements_by_attributes(kwargs.get("tag"), xpath, **kwargs)
        )
    else:
        web_elements = element.get_webelements(xpath, **kwargs)
    if web_elements:
        if CONFIG["SearchMode"]:
            element.draw_borders(web_elements)
        return
    raise QWebElementNotFoundError("No matching element found")


@keyword(tags=["Verification"])
@decorators.timeout_decorator
def verify_no_element(
    xpath: str,
    timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
    **kwargs,
) -> None:
    r"""Wait element can not be found on the page.

    Examples
    --------
    .. code-block:: robotframework

        VerifyNoElement          //*[@id\="do_not_wait_me"]

    This keyword has timeout functionality. If the element is still visible after
    given timeout, error is raised.
    For example.

    .. code-block:: robotframework

       VerifyNoElement          //*[@id\="wait_me"]       20   #waits 20 seconds

    Parameters
    ----------
    xpath : str
        Xpath expression without xpath= prefix. The equal sign "=" must be escaped with a "\\".
    timeout : str | int
        Timeout for the element to disappear. If the element is visible after
        given timeout, error is raised. The str is converted to integer
        using robot.utils.timestr_to_secs. (default 10 seconds)
    kwargs :
        |  Accepted kwargs:
        |       tag : html tag of preferred elemenr -
        |           If tag is used then element is found
        |           by some of it's attribute (xpath is not needed)
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    NoSuchElementException
        Page did contain the element

    Related keywords
    ----------------
    \`VerifyElement\`
    """
    kwargs["element_kw"] = True
    if "tag" in kwargs:
        web_elements = element.get_visible_elements_from_elements(
            element.get_elements_by_attributes(kwargs.get("tag"), xpath, **kwargs)
        )
    else:
        web_elements = element.get_webelements(xpath)
    if not web_elements:
        return
    raise QWebValueError('Page contained element with XPath "{}" after timeout'.format(xpath))


@keyword(tags=["Getters"])
@decorators.timeout_decorator
def get_webelement(
    locator: str,
    anchor: str = "1",
    element_type: Optional[str] = None,
    timeout: Union[int, float, str] = 0,
    all_frames: bool = True,
    **kwargs,
) -> Union[Select, Optional[WebElement], list[WebElement]]:
    # pylint: disable=too-many-branches
    r"""Get Webelement using any Qword -stylish locator.

    Examples
    --------
    Using attributes or xpaths like with ClickElement etc. kw:s without specified
    element_type. Result is a type of list unless **index** or **element_type** is given:

    .. code-block:: robotframework

        ${list of elems}    GetWebelement          click_me      tag=button
        ${list of elems}    GetWebelement          //*[@id\="click_me"]
        ${list of elems}    GetWebelement          xpath\=//*[@id\="click_me"]
        # return elements only from the first frame with matching elements
        ${list of elems}    GetWebelement          xpath\=//*[@id\="click_me"]   all_frames=False

    Get element using element_type attribute to locate element.
    Text elements works as ClickText, VerifyText, GetText etc.:

    .. code-block:: robotframework

        ${elem}      GetWebelement          Log In    element_type=text
        ${elem}      GetWebelement          Contact   element_type=text  anchor=Qentinel
        ${elem}      GetWebelement          Contact   parent=div

    Item, Input, Dropdown, Checkbox elements:

    .. code-block:: robotframework

        ${elem}      GetWebelement          Log In    element_type=item
        ${elem}      GetWebelement          Username  element_type=input
        ${elem}      GetWebelement          Country   element_type=dropdown
        ${elem}      GetWebelement          Gender    element_type=checkbox

    Any element using css selectors:

    .. code-block:: robotframework

        ${elem}      GetWebelement          input[type=button]:nth-child(10)    element_type=css

    All flags are available for using (timeout, anchor, index, visibility, parent, child etc.).
    in same way as you are using those with Qwords like ClickText/Item, TypeText, Dropdown etc.

    Parameters
    ----------
    locator : str
        Visible text, attribute value or Xpath expression with or without xpath= prefix.
        The equal sign "=" must be escaped with a "\\".
    anchor : int
        Used when element_type is defined. Default=1 (first match)
    element_type : string
        Define element type/preferred searching method
        (available types: text, input, checkbox, item, dropdown or css).
    all_frames : bool
        In cases where list is expected to be returned, traverse through all frames
        (True) or stop on the first frame which contains matching elements (False).
        Doesn't have any effect if there are no iframes or if element_type etc. are used.
        Default=True.
    timeout : int
        How long we wait element to appear. Default=10 sec
    kwargs :
        |  Accepted kwargs:
        |       Any available for picked searching method.
        |       See interacting with text, item, input etc. elements from
        |       documentation

    Related keywords
    ----------------
    \`ClickElement\`, \`HoverElement\`, \`TypeText\`
    """
    web_elements: Union[Select, Optional[WebElement], list[WebElement]]
    elem_index = kwargs.get("index", None)
    kwargs["index"] = kwargs.get("index", 1)
    kwargs["timeout"] = timeout
    kwargs["continue_search"] = all_frames
    if element_type:
        if element_type.lower() == "text":
            web_elements = text.get_element_by_locator_text(locator, anchor, **kwargs)
        elif element_type.lower() == "item":
            web_elements = text.get_item_using_anchor(locator, anchor, **kwargs)
        elif element_type.lower() == "dropdown":
            web_elements = dropdown.get_dd_elements_from_all_documents(locator, anchor, **kwargs)
        elif element_type.lower() == "input":
            web_elements = input_.get_input_elements_from_all_documents(locator, anchor, **kwargs)
        elif element_type.lower() == "checkbox":
            web_elements = checkbox.get_checkbox_elements_from_all_documents(
                locator, anchor, **kwargs
            )[0]
        elif element_type.lower() == "css":
            web_elements = element.get_webelement_by_css(locator, **kwargs)
        else:
            msg = (
                f"Invalid 'element_type':'{element_type}'!\n"
                "\tValid types: 'text', 'item', 'dropdown', 'input', 'checkbox', 'css'"
            )
            raise QWebValueError(msg)
        return web_elements

    kwargs["element_kw"] = True
    if "tag" in kwargs:
        web_elements = element.get_visible_elements_from_elements(
            element.get_elements_by_attributes(kwargs.get("tag"), locator, **kwargs)
        )
    else:
        web_element_list = element.get_webelements(locator, **kwargs)
        if elem_index:
            web_elements = element.get_element_by_index(web_element_list, elem_index)  # type: ignore # pylint: disable=line-too-long
        else:
            web_elements = web_element_list
    if web_elements:
        return web_elements
    raise QWebElementNotFoundError("No matching element found")


@keyword(tags=["Getters"])
@decorators.timeout_decorator
def get_attribute(
    locator: str,
    attribute: str,
    anchor: str = "1",
    element_type: Optional[str] = None,
    timeout: Union[int, float, str] = 0,
    **kwargs,
) -> str:
    r"""Get attribute value of an element.

    Examples
    --------
    Using xpaths like with ClickElement etc. kw:s without specified
    element_type. Index must be given if element is not unique:

    .. code-block:: robotframework

        ${attribute_value}  GetAttribute            click_me     id         tag=button
        ${attribute_value}  GetAttribute            //*[@id\="click_me"]    id
        ${attribute_value}  GetAttribute            xpath\=//*[@id\="click_me"] name
        # Get id attribute value from 3rd matching element
        ${attribute_value}  GetAttribute            //button    id  index=3

    GetAttribute using element_type attribute to locate element.
    Text elements works as ClickText, VerifyText, GetText etc.:

    .. code-block:: robotframework

        ${attribute_value}   GetAttribute     Log In    type    element_type=text
        ${attribute_value}   GetAttribute     Contact   id      element_type=text  anchor=Qentinel
        ${attribute_value}   GetAttribute     Contact   class   parent=div

    Item, Input, Dropdown, Checkbox elements:

    .. code-block:: robotframework

        ${attribute_value}  GetAttribute          Log In    id              element_type=item
        ${attribute_value}  GetAttribute          Username  placeholder     element_type=input
        ${attribute_value}  GetAttribute          Country   value           element_type=dropdown
        ${attribute_value}  GetAttribute          Gender    checked         element_type=checkbox

    Any element using css selectors:

    .. code-block:: robotframework

        ${attribute_value}  GetAttribute          input[type=button]   value    element_type=css

    All flags are available for using (timeout, anchor, index, visibility, parent, child etc.).
    in same way as you are using those with Qwords like ClickText/Item, TypeText, Dropdown etc.

    Parameters
    ----------
    locator : str
        Visible text, attribute value or Xpath expression with or without xpath= prefix.
        The equal sign "=" must be escaped with a "\\".
    attribute: str
        Attribute which value we want to get.
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
    value : Value of attribute (true if attribute exist but does not have value)

    Related keywords
    ----------------
    \`VerifyAttribute\`, \`VerifyElement\`
    """
    # remove all_frames from kwargs if given. It's not supported by
    # GetAttribute, but would give error later
    kwargs.pop("all_frames", None)
    webelement = get_webelement(locator, anchor, element_type, timeout, all_frames=False, **kwargs)

    if not webelement:
        raise QWebElementNotFoundError(
            "Could not find element {} with attribute {}".format(locator, attribute)
        )
    if not isinstance(webelement, list):
        return webelement.get_attribute(attribute)

    if len(webelement) == 1:
        return webelement[0].get_attribute(attribute)

    raise QWebValueError(
        "Found {} occurences of locator {}. "
        "Use index etc. to uniquely identify the element".format(len(webelement), locator)
    )


@keyword(tags=["Verification"])
@decorators.timeout_decorator
def verify_attribute(
    locator: str,
    attribute: str,
    value: str,
    anchor: str = "1",
    element_type: Optional[str] = None,
    timeout: Union[int, float, str] = 0,
    **kwargs,
) -> None:
    r"""Verify attribute value of an element.

    Examples
    --------
    Using attributes or xpaths like with ClickElement etc. kw:s without specified
    element_type. If element_type is not specified end result is a type of list:

    .. code-block:: robotframework

        VerifyAttribute     click_me                        id    my_button   tag=button
        VerifyAttribute     //*[@id\="click_me"]            name    click_here
        VerifyAttribute     xpath\=//*[@id\="click_me"]     name    click_here

    GetAttribute using element_type attribute to locate element.
    Text elements works as ClickText, VerifyText, GetText etc.:

    .. code-block:: robotframework

        VerifyAttribute     Log In    id    login       element_type=text
        VerifyAttribute     Contact   value abc         element_type=text  anchor=Qentinel
        VerifyAttribute     Contact   name  contact1    parent=div

    Item, Input, Dropdown, Checkbox elements:

    .. code-block:: robotframework

        VerifyAttribute     Log In    id    login   element_type=item
        VerifyAttribute     Username  placeholder   username    element_type=input
        VerifyAttribute     Country   value     Finland         element_type=dropdown
        VerifyAttribute     Gender    checked   checked         element_type=checkbox

    Any element using css selectors:

    .. code-block:: robotframework

        VerifyAttribute          input[type=button]   value    Click Me     element_type=css

    All flags are available for using (timeout, anchor, index, visibility, parent, child etc.).
    in same way as you are using those with Pacewords like ClickText/Item, TypeText, Dropdown etc.

    In addition, operator performing verification can be given as keyword argument.
    If 'operator' argument is not given, 'equals' is expected. Examples:

    .. code-block:: robotframework

        # Not equal
        VerifyAttribute     //img    data-icon    screen123    operator=not equal
        VerifyAttribute     //img    data-icon    screen123    operator=!=

        # Greater than
        VerifyAttribute    Button3    data-id    7    element_type=Text    operator=greater than
        VerifyAttribute    Button3    data-id    5    element_type=Text    operator=>

        # less than or equal
        # ('operator=less than or equal' also works)
        VerifyAttribute    Button3    data-id    10   element_type=Item   operator=<=

        # contains
        VerifyAttribute    somebutton    id    skim      element_type=Text   operator=contains

    Parameters
    ----------
    locator : str
        Visible text, attribute value or Xpath expression with or without xpath= prefix.
        The equal sign "=" must be escaped with a "\\".
    attribute: str
        Attribute which value we want to get.
    value: str
        Expected attribute value to verify against.
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
        |       documentation
        |
        |       In addition:
        |       operator : str
        |           Which operator use for verification. Possible values:
        |               * 'Equals' or '==' (Default)
        |               * 'Not Equal' or '!='
        |               * 'Less than' or '<'
        |               * 'Greater than' or '>'
        |               * 'Less than or equal' or  '<='
        |               * 'Greater than or equal' or '>='
        |               * 'Contains'
        |               * 'Not Contains'


    Related keywords
    ----------------
    \`GetAttribute\`, \`VerifyElement\`
    """
    attr_val = get_attribute(locator, attribute, anchor, element_type, timeout, **kwargs)
    operator = kwargs.get("operator", "equals")

    try:
        element.operator_verify(attr_val, value, operator)
    except QWebValueError as e:
        raise e


@keyword(tags=["Getters"])
def get_coordinates(
    locator: Union[WebElement, str],
    anchor: str = "1",
    element_type: Optional[str] = None,
    overlay_offset: int = 0,
    timeout: Union[int, float, str] = 0,
    **kwargs,
) -> Dict[str, float]:
    # pylint: disable=too-many-branches
    r"""Gets middle point location (x, y) of the first element matching locator.
    If locator is an instance of WebElement, returns the middle point location of that element.

    This keyword tries to scroll the element into view (top) and then calculates the middle point
    location. If the page has a overlay / top bar that covers the element,
    you can use **overlay_offset** to adjust the scroll amount (see examples).

    Examples
    --------
    Using attributes or xpaths like with ClickElement etc. kw:s without specified
    element_type:

    .. code-block:: robotframework

        &{coords}=    GetCoordinates          click_me      tag=button
        Click Coordinates    ${coords.x}    ${coords.y}

        &{coords}=    GetCoordinates          //*[@id\="click_me"]
        &{coords}=    GetCoordinates          xpath\=//*[@id\="click_me"]


    Using element_type attribute to locate element.
    Text elements works as ClickText, VerifyText, GetText etc.:

    .. code-block:: robotframework

        &{coords}=    GetCoordinates     Log In    id    login       element_type=text
        &{coords}=    GetCoordinates     Contact   value abc         element_type=text  anchor=Name
        &{coords}=    GetCoordinates     Contact   name  contact1    parent=div
        Click Coordinates    ${coords.x}    ${coords.y}

    Item, Input, Dropdown, Checkbox elements:

    .. code-block:: robotframework

        &{coords}=    GetCoordinates     Log In    id    login   element_type=item
        &{coords}=    GetCoordinates     Username  placeholder   username    element_type=input
        &{coords}=    GetCoordinates     Country   value     Finland         element_type=dropdown
        &{coords}=    GetCoordinates     Gender    checked   checked         element_type=checkbox
        Click Coordinates    ${coords.x}    ${coords.y}

    Using previously fetched WebElement instance:

    .. code-block:: robotframework

        ${element}=   GetWebElement      Log In    id    login   element_type=item
        &{coords}=    GetCoordinates     ${element}
        Click Coordinates    ${coords.x}    ${coords.y}

    If a page has an overlay that covers the element, you can use overlay_offset
    to adjust the scroll:

    .. code-block:: robotframework

        # This will scroll the element into view and adjust the scroll (up) by 50 pixels
        &{pos}=    GetCoordinates     Log In    id    login   element_type=item   overlay_offset=50
        Click Coordinates    ${pos.x}    ${pos.y}


    Parameters
    ----------
    locator : str
        Visible text, attribute value Xpath expression or WebElement.
        See GetWebElement for more information.
    anchor : int
        Used when element_type is defined. Default=1 (first match)
    element_type : string
        Define element type/preferred searching method
        (available types: text, input, checkbox, item, dropdown or css).
    overlay_offset: int
        A positive integer representing the offset to adjust the scroll position
        if a top bar or overlay obscures the element.
        Typically, this is the height of the top overlay. Default = 0.

    timeout : int
        How long we wait element to appear. Default=10 sec
    kwargs :
        |  Accepted kwargs:
        |       Any available for picked searching method.
        |       See interacting with text, item, input etc. elements from
        |       documentation

    Returns
    -------
    dict: A dictionary with the coordinates `{"x": float, "y": float}`.

    Related keywords
    ----------------
    \`ClickElement\`, \`HoverElement\`, \`TypeText\`, \`ClickCoordinates\`
    """
    kwargs.pop("all_frames", None)
    webelement: Union[WebElement, list[WebElement]]

    if overlay_offset < 0:
        raise QWebValueError(f"The overlay_offset cannot be negative ({overlay_offset}).")
    # webelement given as a locator
    if isinstance(locator, WebElement):
        webelement = locator
    else:
        webelement = get_webelement(locator,
                                    anchor,
                                    element_type,
                                    timeout,
                                    all_frames=False,
                                    **kwargs)

    # return first matching element
    webelement = webelement[0] if isinstance(webelement, list) else webelement

    try:

        # scroll element into view and adjust scroll if needed
        scrolled_position = webelement.location_once_scrolled_into_view
        actions.scroll_overlay_adjustment(overlay_offset)

    except Exception as e:
        raise QWebValueError(f"Could not scroll element {locator} into view. Error: {e}") from e

    # Calculate the coordinates at the center of the element + overlay height
    size = webelement.size
    x = scrolled_position['x'] + size["width"] / 2
    y = scrolled_position['y'] + overlay_offset + size["height"] / 2

    return {"x": x, "y": y}
