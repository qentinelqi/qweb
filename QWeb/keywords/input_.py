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
"""Keywords for input elements.

Input elements are those in which one can input text in.
"""
from __future__ import annotations
from typing import Union
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from robot.api import logger
from robot.api.deco import keyword
from pyautogui import hotkey
from QWeb.internal.exceptions import QWebFileNotFoundError, QWebValueError
from QWeb.internal import javascript, secrets, actions, util
from QWeb.internal import element, input_, download, decorators
from QWeb.internal.input_handler import INPUT_HANDLER as input_handler
from QWeb.keywords import browser


@keyword(tags=("Config", "Input"))
def set_input_handler(input_method: str) -> None:
    """*DEPRECATED!!* Use keyword `SetConfig` instead.

    Set input handler.

    Default handler is "selenium" which uses Selenium librarys
    methods clear() and send_keys(). These methods assume that
    the web element is writable (enabled). Inserts tab character
    at the end of text.

    Alternative writer "raw" uses pyautogui to input text directly
    without checking the web element state. This version is intended
    to be used when the web page doesn't update input element status
    Selenium compliant way.

    Examples
    --------
    .. code-block:: robotframework

         Set input handler    raw
         Set input handler    selenium

    Parameters
    ----------
    input_method : str
        Input method used by input handler, "selenium" or "raw".

    """
    input_handler.input_method = input_method


@keyword(tags=("Config", "Input"))
def set_line_break(key: str) -> str:
    r"""*DEPRECATED!!* Use keyword `SetConfig` instead."""
    old_line_break_key = input_handler.line_break_key
    input_handler.line_break_key = key
    return old_line_break_key


secrets.add_filter("Type Secret3", 1, "hint")


def type_secret3(locator: str,
                 input_text: str,
                 anchor: str = "1",
                 timeout: Union[int, float, str] = 0,
                 index: int = 1,
                 **kwargs) -> None:
    """Type sensitive information such as personal data.

    the first 1 or 3 digits of the secret value are displayed
    in the logfile, otherwise functionality is the same as Type Secret.

    Generally all secret credentials in Robot FW scripts should
    be provided as external variables. Secrets must not be
    stored directly to test script and not even to version control
    system.

    Examples
    --------
    .. code-block:: robotframework

        # NAME is set outside the script
        # Provide this to Robot FW as follows:
        # robot --variable NAME:janedoe test.robot
        TypeSecret3      name    ${NAME}
        TypeSecret3      r1c1    ${NAME} #table
    """
    length = (len(input_text))
    if length > 4:
        logger.info('SECRET: {}'.format(input_text[:3]) + (length - 3) * '*')
    else:
        logger.info('SECRET: {}'.format(input_text[:1]) + (length - 1) * '*')
    type_text(locator, input_text, anchor, timeout=timeout, index=index, **kwargs)


# Filter out input_text parameter in type_secret
secrets.add_filter("Type Secret", 1, None)


@keyword(tags=("Input", "Interaction"))
def type_secret(locator: str,
                input_text: str,
                anchor: str = "1",
                timeout: Union[int, float, str] = 0,
                index: int = 1,
                **kwargs) -> None:
    r"""Type secret information such as password.

    Logging in start_keyword and end_keyword is filtered,
    otherwise functionality is the same as TypeText.

    Generally all secret credentials in Robot FW scripts should
    be provided as external variables. Secrets must not be
    stored directly to test script and not even to version control
    system.

    Examples
    --------
    .. code-block:: robotframework

        # PASSWD is set outside the script
        # Provide this to Robot FW as follows:
        # robot --variable PASSWD:mypass123 test.robot
        TypeSecret            password    ${PASSWD}
        TypeSecret            r1c1        ${PASSWD}  #table

    Related keywords
    ----------------
    \`TypeText\`
    """
    type_text(locator, input_text, anchor, timeout=timeout, index=index, **kwargs)


@keyword(tags=("Input", "Interaction"))
@decorators.timeout_decorator
def type_text(locator: Union[WebElement, str],
              input_text: str,
              anchor: str = "1",
              timeout: Union[int, float, str] = 0,
              index: int = 1,
              **kwargs) -> None:
    r"""Type given text to a text field.

    First look through if there are any input fields that have the
    locator as a placeholder. If not then locates the input field by
    which is closest to the locator text.

    When input field is found, it is first cleared of all text and after
    that the text is input.

    Simple Example
    --------------
    .. code-block:: robotframework

         TypeText            username    Qentinel


    Parameters
    ----------
    locator : str | selenium.webdriver.remote.webelement.WebElement
        Text that locates the input field. The input field that is closest
        to the text is selected. Also one can use xpath by adding xpath= prefix
        and then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
        Can also be a WebElement instance returned by GetWebElement keyword or javascript.
    input_text : str
        Text that will be written in the input field
    anchor : str
        Index number or text near the input field's locator element.
        If the page contains many places where the locator is then anchor is used
        to select the wanted item. Index number selects the item from the list
        of matching entries starting with 1. Text selects the entry with the closest
        distance.
    timeout : str | int
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If table cell contains more than one input elements or if there is some kind of
        nested structure inside of given input index may needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       check : bool(True/False)
        |       - Shortcut to switch CheckInputValue on or off for one time use.
        |       - If CheckInputValue is used, use expected parameter when expected value
        |       is different than written value. Expected: str | int
        |       click : bool(True/False)
        |       - Shortcut to switch ClickToFocus on or off for one time use.
        |       - If click is set to True, input field is focused by clicking it before typing.
        |       - CheckInputValue defines if TypeText verifies input field value after it is typed.
        |       - Default is Off. Valid parameters are On, True, Off and False.
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match
        |       clear_key: key or character
        |       - used generally if there's problems clearing input field with default methods
        |       - sets what key or key combination is is used to clear the input field
        |       - using clear_key will set clear key
        |       - enclose special keys in curly brackets, for example {CONTROL + a} or {BACKSPACE}
        |       - corresponding configuration parameter is ClearKey

    Examples with settings
    ----------------------
    .. code-block:: robotframework

         SetConfig          CheckInputValue     True
         SetConfig          CheckInputValue     On
         TypeText            username           Qentinel


    SetConfig LineBreak defines what kind of line break is typed after input text. Default is
    tab key.

    .. code-block:: robotframework

        SetConfig           LineBreak   None
        TypeText            username    Qentinel
        TypeText            someattr    Qentinel

    Examples with table
    -------------------


    (Pick table with use table keyword first):

    .. code-block:: robotframework

        TypeText            r1c1        Qentinel
        TypeText            r-1c-1      Qentinel  #last row, last cell
        TypeText            r?Robot/c3  Qentinel  #row that contains text Robot, cell c3

    More Examples
    -------------
    .. code-block:: robotframework

        TypeText            company     Qentinel    clear_key={BACKSPACE}
        TypeText            company     Qentinel    clear_key={CONTROL + a}
        # same thing with using SetConfig
        SetConfig           ClearKey    {BACKSPACE}
        TypeText            company     Qentinel
        SetConfig           ClearKey    {CONTROL + a}
        TypeText            company     Qentinel
        # using WebElement instance
        ${elem}=            GetWebElement  //input[@title\="Search"]
        TypeText            ${elem}     Text to search for
        # Type to input in shadow DOM input
        SetConfig           ShadowDOM   True
        TypeText            Search      Test

    Related keywords
    ----------------
    \`PressKey\`, \`TypeSecret\`, \`TypeTexts\`, \`WriteText\`
    """
    if isinstance(locator, WebElement):
        input_element = locator
    else:
        input_element = input_.get_input_elements_from_all_documents(locator,
                                                                     anchor,
                                                                     timeout=timeout,
                                                                     index=index,
                                                                     **kwargs)
    actions.write(input_element, str(input_text), timeout=timeout, **kwargs)


@keyword(tags=("File", "Input", "Interaction"))
@decorators.timeout_decorator
def type_texts(input_texts: Union[dict[str, str], str],
               timeout: Union[int, float, str] = '0') -> None:
    r"""Type text to multiple fields.

    Accepts a .txt file or Robot FW dictionary as a parameter. If using a text file, the locator
    and the text should be separated with a comma on each row.

    Examples
    --------
    .. code-block:: robotframework

        TypeTexts               list_of_locators_and_texts.txt
        TypeTexts               C:/Users/pace/Desktop/textfile.txt

        ${cool_dict}=           Create Dictionary    Name=Jane    Email=janedoe@iddqd.com
        ...                     Phone=04049292243923     Address=Yellow street 33 C 44
        TypeTexts               ${cool_dict}

    Related keywords
    ----------------
    \`PressKey\`, \`TypeSecret\`, \`TypeText\`, \`WriteText\`
    """
    if isinstance(input_texts, dict):
        for locator in input_texts:
            logger.info('Typing "{}", locator "{}"'.format(locator, input_texts[locator]))
            type_text(locator, input_texts[locator])
    elif input_texts.endswith('.txt') or input_texts.endswith('.csv'):
        file = download.get_path(input_texts)
        with open(file, 'rb') as txt_file:
            params = [line.rstrip() for line in txt_file]
            for x_bytes in params:
                x_str_list = x_bytes.decode('utf-8').split(',')
                locator, text = x_str_list[0].strip(), x_str_list[1].strip()
                logger.info('Typing "{}", locator "{}"'.format(text, locator))
                type_text(locator, text, timeout=timeout)
    else:
        raise QWebValueError('Unknown input value. Text file or dictionary required.')


@keyword(tags=("Input", "Verification"))
@decorators.timeout_decorator
def verify_input_value(locator: Union[WebElement, str],
                       expected_value: str,
                       anchor: str = "1",
                       timeout: Union[int, float, str] = 0,
                       index: int = 1,
                       **kwargs) -> None:
    r"""Verify input field has given value.

    Examples
    --------
    .. code-block:: robotframework

        VerifyInputValue    Username          Qentinel
        VerifyInputValue    Phone Nro         0401234567

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        VerifyInputValue     r1c1        0401234567
        VerifyInputValue     r-1c-1      Qentinel  #last row, last cell
        VerifyInputValue     r?Robot/c3  Qentinel  #row that contains text Robot, cell c3

    Parameters
    ----------
    locator : str
        Text that locates the input field. The input field that is closest
        to the text is selected. Also one can use xpath by adding xpath= prefix
        and then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
    expected_value : str
        Text that the input field should contain.
    anchor : str
        Index number or text near the input field's locator element.
        If the page contains many places where the locator is then anchor is used
        to select the wanted item. Index number selects the item from the list
        of matching entries starting with 1. Text selects the entry with the closest
        distance.
    timeout : str
        How long we find element before failing. Default 10 (seconds)
    index : int
        If table cell contains more than one input elements or if there is some kind of
        nested structure inside of given input index may needed. Default = 1 (first)
    kwargs :
        |   Accepted kwargs :
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    ValueError
        If the input value is not the same

    Related keywords
    ----------------
    \`GetInputValue\`, \`VerifyInputElement\`, \`VerifyInputStatus\`, \`VerifyInputValues\`
    """
    if isinstance(locator, WebElement):
        input_element = locator
    else:
        input_element = input_.get_input_elements_from_all_documents(locator,
                                                                     anchor,
                                                                     timeout=timeout,
                                                                     index=index,
                                                                     **kwargs)
    actions.compare_input_values(input_element, expected_value, timeout=timeout)


@keyword(tags=("Input", "Verification"))
@decorators.timeout_decorator
def verify_input_values(input_values: Union[dict[str, str], str],
                        timeout: Union[int, float, str] = '0') -> None:
    r"""Verify input fields have given values.

    Accepts a .txt file or Robot FW dictionary as a parameter. If using a text file, the locator
    and the expected value should be separated with a comma on each row.

    Examples
    --------
    .. code-block:: robotframework

        VerifyInputValues       list_of_locators_and_values.txt
        VerifyInputValues       C:/Users/pace/Desktop/textfile.txt

        ${cool_dict}=           Create Dictionary    Name=Jane    Email=janedoe@iddqd.com
        ...                     Phone=04049292243923     Address=Yellow street 33 C 44
        VerifyInputValues       ${cool_dict}

    Related keywords
    ----------------
    \`VerifyInputValue\`
    """
    if isinstance(input_values, dict):
        for locator in input_values:
            logger.info('Locator: {}, Expected value: {}'.format(locator, input_values[locator]),
                        also_console=True)
            verify_input_value(locator, input_values[locator])
    elif input_values.endswith('.txt') or input_values.endswith('.csv'):
        file = download.get_path(input_values)
        with open(file, 'rb') as txt_file:
            params = [line.rstrip() for line in txt_file]
            for x_bytes in params:
                x_str_list = x_bytes.decode('utf-8').split(',')
                locator, value = x_str_list[0].strip(), x_str_list[1].strip()
                logger.info('Locator: {}, Expected value: {}'.format(locator, value),
                            also_console=True)
                verify_input_value(locator, value, timeout=timeout)
    else:
        raise QWebValueError('Unknown input value. Text file or dictionary required.')


@keyword(tags=("Input", "Verification"))
@decorators.timeout_decorator
def verify_input_status(locator: str,
                        status: str,
                        anchor: str = "1",
                        timeout: Union[int, float, str] = 0,
                        index: int = 1,
                        **kwargs) -> None:
    r"""Verify input field is enabled or disabled.

    In other words verify can user interact with an input field or not.
    Element is considered to be disabled if disabled or readonly attribute exists


    Examples
    --------
    .. code-block:: robotframework

        VerifyInputStatus   Password        Enabled
        VerifyInputStatus   SSN             Disabled
        VerifyInputStatus   SSN             ReadOnly

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        VerifyInputStatus    r1c1        Enabled
        VerifyInputStatus    r-1c-1      Disabled  #last row, last cell

    Parameters
    ----------
    locator : str
        Text that locates the input field. The input field that is closest
        to the text is selected. Also one can use xpath by adding xpath= prefix
        and then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
    status : str
        Status for the input field. Either enabled, readonly or disabled.
    anchor : str
        Index number or text near the input field's locator element.
        If the page contains many places where the locator is then anchor is used
        to select the wanted item. Index number selects the item from the list
        of matching entries starting with 1. Text selects the entry with the closest
        distance.
    timeout : str | int
        How long we find element before failing. Default 10 (seconds)
    index : int
        If table cell contains more than one input elements or if there is some kind of
        nested structure inside of given input index may needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match

    Raises
    ------
    QWebValueError
        If the field interaction is not the same

    Related keywords
    ----------------
    \`GetInputValue\`, \`VerifyInputElement\`, \`VerifyInputValue\`, \`VerifyInputValues\`
    """
    input_element = input_.get_input_elements_from_all_documents(locator,
                                                                 anchor,
                                                                 timeout=timeout,
                                                                 index=index,
                                                                 enable_check=True,
                                                                 **kwargs)
    if status.lower() == "enabled":
        if not element.is_enabled(input_element) or element.is_readonly(input_element):
            raise QWebValueError('The input field was disabled')
    elif status.lower() == "disabled":
        if element.is_enabled(input_element):
            raise QWebValueError('The input field was enabled')
    elif status.lower() == "readonly":
        if not element.is_readonly(input_element):
            raise QWebValueError('readonly attr not found')
    else:
        raise QWebValueError('Unkown status: "{}"'.format(status))


@keyword(tags=("Input", "Verification"))
@decorators.timeout_decorator
def verify_input_element(locator: str,
                         anchor: str = "1",
                         timeout: Union[int, float, str] = 0,
                         index: int = 1,
                         **kwargs) -> None:
    r"""Verify that input element exist.

    Examples
    --------
    .. code-block:: robotframework

        VerifyInputElement   Username

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

        VerifyInputElement   r1c1

    With anchor

    .. code-block:: robotframework

        VerifyInputElement   Password       Username
        VerifyInputElement   r?Qentinel/c3  Robot   #row contains texts Qentinel and Robot, cell 3

    Parameters
    ----------
    locator : str
        Text that locates the element.
    anchor : str
        Text near the checkbox's locator element. If the page contains many
        places where the locator text is then anchor is used to get the
        one that is closest to it. (default None)
    timeout : str | int
        How long we try to find element before failing. Default 10 (seconds)
    index : int
        If table cell contains more than one input elements or if there is some kind of
        nested structure inside of given input index may needed. Default = 1 (first)
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
    \`GetInputValue\`, \`VerifyInputStatus\`, \`VerifyInputValue\`, \`VerifyInputValues\`
    """
    input_element = input_.get_input_elements_from_all_documents(locator,
                                                                 anchor,
                                                                 timeout=timeout,
                                                                 index=index,
                                                                 **kwargs)
    if input_element:
        return


@keyword(tags=("Input", "Getters"))
@decorators.timeout_decorator
def get_input_value(locator: str,
                    anchor: str = "1",
                    timeout: Union[int, float, str] = 0,
                    index: int = 1,
                    **kwargs) -> Union[int, float, str]:
    r"""Get input value from input field.

    Examples
    --------
    .. code-block:: robotframework

       ${value}=    GetInputValue    OrderNro
       ${value}=    GetInputValue    OrderNro       Submit
       ${value}=    GetInputValue    someattrs      from_end=3  int=True
       #Return empty if there is not value in input element:
       ${value}=    GetInputValue    OrderNro       blind=True

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

         ${value}=    GetInputValue    r1c1
         ${value}=    GetInputValue    r?OrderNro/c1    My Order

    Parameters
    ----------
    locator : str
        Text that locates the input field. The input field that is closest
        to the text is selected. Also one can use xpath by adding xpath= prefix
        and then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
    anchor : str
        Index number or text near the input field's locator element.
        If the page contains many places where the locator is then anchor is used
        to select the wanted item. Index number selects the item from the list
        of matching entries starting with 1. Text selects the entry with the closest
        distance.
    timeout : str | int
        How long we find element before failing. Default 10 (seconds)
    index : int
        If table cell contains more than one input elements or if there is some kind of
        nested structure inside of given input index may needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.
        |       between : str/int - Start???End - Return all chars between texts Start and End.
        |       from_start : int - Return x amount of chars. Starting from first char
        |       from_end : int - Return x amount of chars. Starting from last char
        |       include_locator : True - Starting text is part of returned string
        |       exclude_post : False - Ending text is part of returned string
        |       int : True - Return integer instead of string
        |       float : int - Return float instead of string
        |       partial_match: True. If element is found by it's attribute set partial_match
        |       to True to allow partial match
        |       blind : True - Return empty instead of error if input element is empty

    Related keywords
    ----------------
    \`VerifyInputElement\`, \`VerifyInputStatus\`, \`VerifyInputValue\`, \`VerifyInputValues\`
    """
    input_element = input_.get_input_elements_from_all_documents(locator,
                                                                 anchor,
                                                                 timeout=timeout,
                                                                 index=index,
                                                                 **kwargs)
    val = actions.input_value(input_element, timeout=timeout, **kwargs)
    return util.get_substring(val, **kwargs)


@keyword(tags=("File", "Input", "Interaction"))
@decorators.timeout_decorator
def upload_file(locator: str,
                filename: str,
                anchor: str = "1",
                timeout: Union[int, float, str] = 0,
                index: int = 1,
                **kwargs) -> None:
    r"""Upload file.

    Examples
    --------
    .. code-block:: robotframework

       UploadFile   Upload      text.txt
       UploadFile   Foo         C:/path/to/file/test.pdf
       UploadFile   1           text.txt #Using index as locator

    With table(Pick table with use table keyword first):

    .. code-block:: robotframework

       UploadFile   r1c1        text.txt

    Parameters
    ----------
    locator : str
        Text or index that locates the upload element.
    filename : file to upload
        Default folders = users/downloads, project_dir/files or ${EXECDIR}/\*\*/files
    anchor : str
        Index number or text near the input field's locator element.
        If the page contains many places where the locator is then anchor is used
        to select the wanted element. Index number selects the item from the list
        of matching entries starting with 1. Text selects the entry with the closest
        distance.
    timeout : str | int
        How long we find element before failing. Default 10 (seconds)
    index : int
        If table cell contains more than one input elements or if there is some kind of
        nested structure inside of given input index may needed. Default = 1 (first)
    kwargs :
        |  Accepted kwargs:
        |       limit_traverse : False. If limit traverse is set to false we are heading up to
        |       fifth parent element if needed when finding relative input element for some label.

    Raises
    ------
    ValueError: File not found

    Related keywords
    ----------------
    \`SaveFile\`
    """
    kwargs['css'] = kwargs.get('css', '[type="file"]')
    kwargs['upload'] = util.par2bool(kwargs.get('upload', True))
    filepath = download.get_path(filename)
    if filepath:
        input_element = input_.get_input_elements_from_all_documents(locator,
                                                                     anchor,
                                                                     timeout=timeout,
                                                                     index=index,
                                                                     **kwargs)
        input_element.send_keys(str(filepath.resolve()))
        return
    raise QWebFileNotFoundError(
        'Unable to find file {}. Tried from project/files and users/downloads'.format(filename))


@keyword(tags=("Input", "Interaction"))
@decorators.timeout_decorator
def press_key(locator: str,
              key: str,
              anchor: str = "1",
              timeout: Union[int, float, str] = 0,
              **kwargs) -> None:
    r"""Simulate user pressing keyboard key on element identified by "locator".

    The parameter "key" is either a single character or a keyboard key combination
    surrounded by '{ }'.

    If ${EMPTY} is given as a locator, "global" hotkey combination is sent and handled by the OS.

    Examples
    --------
    .. code-block:: robotframework

        PressKey    text_field     q
        PressKey    text_field     {ENTER}
        PressKey    text_field     {CONTROL + A}    # Select all
        PressKey    text_field     {CONTROL + C}    # Copy selected text
        PressKey    other_field    {CONTROL + V}    # Paste copied text
        PressKey    text_field     {PASTE}          # Paste copied text

        # Send ESC keypress without locator and let OS decide how it's consumed
        # on Windows this opens task manager
        PressKey    ${EMPTY}       {CTRL + SHIFT + ESC}

    Notes
    -----
    Below is a list of supported keys that can be sent to a web element,
    in addition to keys that consist of a single character (like 'c' or '?'):

    'ADD', 'ALT', 'ARROW_DOWN', 'ARROW_LEFT', 'ARROW_RIGHT', 'ARROW_UP', 'BACKSPACE', 'BACK_SPACE',
    'CANCEL', 'CLEAR',COMMAND', 'CONTROL', 'DECIMAL', 'DELETE', 'DIVIDE', 'DOWN', 'END', 'ENTER',
    'EQUALS', 'ESCAPE', 'F1', 'F10', 'F11', 'F12', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9',
    'HELP', 'HOME', 'INSERT', 'LEFT', 'LEFT_ALT', 'LEFT_CONTROL', 'LEFT_SHIFT', 'META', 'MULTIPLY',
    'NULL', 'NUMPAD0', 'NUMPAD1', 'NUMPAD2', 'NUMPAD3', 'NUMPAD4', 'NUMPAD5', 'NUMPAD6', 'NUMPAD7',
    'NUMPAD8', 'NUMPAD9', 'PAGE_DOWN', 'PAGE_UP', 'PAUSE', 'RETURN', 'RIGHT', 'SEMICOLON',
    'SEPARATOR', 'SHIFT', 'SPACE', 'SUBTRACT', 'TAB', 'UP', 'ZENKAKU_HANKAKU'


    Notes
    -----
    Below is a list of supported keys names that can be used as "global" hotkeys,
    in addition to keys that consist of a single character (like 'c' or '?'):

    'ACCEPT', 'ADD', 'ALT', 'ALTLEFT', 'ALTRIGHT', 'APPS', 'BACKSPACE', 'BROWSERBACK',
    'BROWSERFAVORITES', 'BROWSERFORWARD', 'BROWSERHOME', 'BROWSERREFRESH', 'BROWSERSEARCH',
    'BROWSERSTOP', 'CAPSLOCK', 'CLEAR','CONVERT', 'CTRL', 'CTRLLEFT', 'CTRLRIGHT', 'DECIMAL',
    'DEL', 'DELETE', 'DIVIDE', 'DOWN', 'END', 'ENTER', 'ESC', 'ESCAPE', 'EXECUTE', 'F1', 'F10',
    'F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19','F2', 'F20', 'F21', 'F22',
    'F23', 'F24', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'FINAL', 'FN', 'HANGUEL', 'HANGUL',
    'HANJA', 'HELP', 'HOME', 'INSERT', 'JUNJA', 'KANA', 'KANJI', 'LAUNCHAPP1', 'LAUNCHAPP2',
    'LAUNCHMAIL', 'LAUNCHMEDIASELECT', 'LEFT', 'MODECHANGE', 'MULTIPLY', 'NEXTTRACK', 'NONCONVERT',
    'NUM0', 'NUM1', 'NUM2', 'NUM3', 'NUM4', 'NUM5', 'NUM6', 'NUM7', 'NUM8', 'NUM9', 'NUMLOCK',
    'PAGEDOWN', 'PAGEUP', 'PAUSE', 'PGDN', 'PGUP', 'PLAYPAUSE', 'PREVTRACK', 'PRINT',
    'PRINTSCREEN', 'PRNTSCRN', 'PRTSC', 'PRTSCR', 'RETURN', 'RIGHT', 'SCROLLLOCK', 'SELECT',
    'SEPARATOR', 'SHIFT', 'SHIFTLEFT', 'SHIFTRIGHT', 'SLEEP', 'SPACE', 'STOP', 'SUBTRACT',
    'TAB', 'UP', 'VOLUMEDOWN', 'VOLUMEMUTE', 'VOLUMEUP', 'WIN', 'WINLEFT', 'WINRIGHT, 'YEN',
    'COMMAND', 'OPTION', 'OPTIONLEFT', 'OPTIONRIGHT'


    Related keywords
    ----------------
    \`TypeSecret\`, \`TypeText\`, \`WriteText\`
    """
    # no locator given, "global" hotkey
    if not locator:
        try:
            checked_key = input_handler.check_key_pyautogui(key)
        except AttributeError as e:
            logger.console(e)
            raise QWebValueError(f'Could not find key: {key}') from e
        return hotkey(*checked_key) if isinstance(checked_key, list) else hotkey(checked_key)

    driver = browser.return_browser()
    action = ActionChains(driver)
    try:
        input_element = input_.get_input_elements_from_all_documents(locator,
                                                                     anchor,
                                                                     timeout=timeout,
                                                                     index=1,
                                                                     **kwargs)
        key = input_handler.check_key(key)  # type: ignore[assignment]

        # COMMAND key workaround on safari
        # supports normal text field CMD operations only
        # (i.e. CMD+C, CMD+A, CMD+V etc.)
        if len(key) == 2 and key[0] == '\ue03d' and util.is_safari():
            javascript.execute_javascript("arguments[0].focus();", input_element)
            action.key_down(key[0]) \
                  .send_keys(key[1]) \
                  .key_up(key[0]).perform()
        else:
            input_element.send_keys(key)
    except AttributeError as e:
        logger.console(e)
        raise QWebValueError('Could not find key "{}"'.format(key)) from e
    return None


@keyword(tags=("Browser", "Interaction"))
def scroll(locator: str,
           direction: str = 'pagedown',
           timeout: Union[int, float, str] = 0, **kwargs) -> None:
    r"""Scrolls the page/element to given direction.

    Examples
    --------
    .. code-block:: robotframework

        # Scroll page down default value (one page)
        Scroll  //html

        # Scroll page up
        Scroll  //html      page_up

        # Scroll page right
        Scroll  //html      right

        # Scroll to the bottom of a list using attribute value and tag
        Scroll  uiScroller    bottom    tag=div

        # Scroll to the top of a list using attribute value and tag
        Scroll  uiScroller    top    tag=div

        # Scroll (page) down 3 times in a list
        Repeat Keyword     3 times    Scroll    uiScroller   down    tag=div

    Parameters
    ----------
    locator : str
        Xpath to scrollable element or attribute value of an scrollable element.
    direction : str
        Direction to scroll to (down, up, left, right, top, bottom, page_down, page_up).
          * Down/up/left/right map to respective ARROW keys.
          * Top/Bottom map to HOME & END keys.
          * Page_up/Page_down map to PAGE_UP and PAGE_DOWN keys.
    timeout : int
        How long to scroll in seconds, before timing out.

    Raises
    ------
    QWebValueError
        If direction is not given in correct format.
    QWebElementNotFoundError
        If the given scrollable element is not found.

    Related keywords
    ----------------
    \`ScrollTo\`, \`ScrollText\`
    """

    keys = {"pagedown": "{PAGE_DOWN}",
            "pageup": "{PAGE_UP}",
            "top": "{HOME}",
            "bottom": "{END}",
            "up": "{ARROW_UP}",
            "down": "{ARROW_DOWN}",
            "left": "{ARROW_LEFT}",
            "right": "{ARROW_RIGHT}"}

    try:
        key = keys[direction.lower().replace("_", "")]
    except KeyError as e:
        raise QWebValueError("""Unknown 'direction'. Valid values are: page_down,
                             page_up, down, up, left, right, top, bottom""") from e
    press_key(locator, key, timeout=timeout, **kwargs)
