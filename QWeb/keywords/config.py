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

from QWeb.internal.config_defaults import CONFIG


def set_config(par, val):
    r"""Set configuration parameter to given value. Return previous value.

    ---
    Parameter: LogScreenshot

    Enables or disables logging screenshots when keyword fails.
    Default is screenshot (True). False disables screenshots from logs when keyword fails.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    LogScreenshot         False
        SetConfig    LogScreenshot         True


    ---
    Parameter: ScreenshotType

    Defines how screenshot is taken. Default is normal screenshot.
    "html" saves page as html frame in test log. "all" saves both image and html page.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    ScreenshotType        html
        SetConfig    ScreenshotType        screenshot
        SetConfig    ScreenshotType        all


    ---
    Parameter: OSScreenshots

    Defines if screenhots are taken using selenium's or operating system's functionalities.
    Default is selenium screenshot (False).

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    OSScreenshots        True
        SetConfig    OSScreenshots        False

    ---
    Parameter: CssSelectors

    Use CSS selectors for finding elements.

    CSS selectors is optional way to find elements that
    are difficult to catch by default selectors. Typically
    those elements are inputs, checkboxes and dropdowns
    without placeholder texts.

    With CSS selectors the detection is tried with:

    * Placeholder or tooltip

    * Label with 'for' attribute

    * DOM traversing to detect sibling element

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    CssSelectors       on
        TypeText     MyLocator   Robot
        SetConfig    CssSelectors       off


    ---
    Parameter: SearchDirection

    Set search direction for element search.

    Search direction is "up", "down", "left", "right" and "closest"

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    SearchDirection       right
        TypeText     MyLocator   Robot
        SetConfig    SearchDirection       closest

    ---
    Parameter: LineBreak

    Set key to be pressed after text is written to input field.

    By default tab key (\ue004) is pressed

    Values, that are mapped for selenium keys are:

    ================  ======
    Key               Value
    ================  ======
    null              \ue000
    cancel            \ue001
    help              \ue002
    backspace         \ue003
    tab               \ue004
    clear             \ue005
    return            \ue006
    enter             \ue007
    shift             \ue008
    left_shift        \ue008
    control           \ue009
    left_control      \ue009
    alt               \ue00A
    left_alt          \ue00A
    pause             \ue00B
    escape            \ue00C
    space             \ue00D
    page_up           \ue00E
    page_down         \ue00F
    end               \ue010
    home              \ue011
    left              \ue012
    arrow_left        \ue012
    up                \ue013
    arrow_up          \ue013
    right             \ue014
    arrow_right       \ue014
    down              \ue015
    arrow_down        \ue015
    insert            \ue016
    delete            \ue017
    semicolon         \ue018
    equals            \ue019
    numpad0           \ue01A
    numpad1           \ue01B
    numpad2           \ue01C
    numpad3           \ue01D
    numpad4           \ue01E
    numpad5           \ue01F
    numpad6           \ue020
    numpad7           \ue021
    numpad8           \ue022
    numpad9           \ue023
    multiply          \ue024
    add               \ue025
    separator         \ue026
    subtract          \ue027
    decimal           \ue028
    divide            \ue029
    f1                \ue031
    f2                \ue032
    f3                \ue033
    f4                \ue034
    f5                \ue035
    f6                \ue036
    f7                \ue037
    f8                \ue038
    f9                \ue039
    f10               \ue03A
    f11               \ue03B
    f12               \ue03C
    meta              \ue03D
    right_shift       \ue050
    right_control     \ue051
    right_alt         \ue052
    right_meta        \ue053
    numpad_page_up    \ue054
    numpad_page_down  \ue055
    numpad_end        \ue056
    numpad_home       \ue057
    numpad_left       \ue058
    numpad_up         \ue059
    numpad_right      \ue05A
    numpad_down       \ue05B
    numpad_insert     \ue05C
    numpad_delete     \ue05D
    ================  ======

    Examples
    --------
    .. code-block:: robotframework

        SetConfig   LineBreak    \ue004    # Tab key
        SetConfig   LineBreak    \ue007    # Enter key
        SetConfig   LineBreak    ${EMPTY}  # Do not send anything

    ---
    Parameter: ClearKey

    Set key to be pressed before text is written to input field.

    By default uses webdrivers clear method to clear element.

    Available values are same as with LineBreak. Some keyboard shortcuts
    also available. Some examples from link below:
    https://turbofuture.com/computers/keyboard-shortcut-keys:

    Examples
    --------
    .. code-block:: robotframework

        SetConfig   ClearKey     None           # Uses clear method (=default)
        SetConfig   ClearKey     {NULL}         # Does nothing
        SetConfig   ClearKey     {CONTROL + A}  # Select all and overwrite
        # One time use:
        TypeText    username    Robot       clear_key={CONTROL + A}

    ---

    Parameter: CheckInputValue

    Check that real value matches to preferred value after TypeText.

    If value is not match we try to re type (three times before fail)
    This is optional feature. Default = false.
    Use with caution on elements where webdriver has tendency to lost focus
    and some part of the preferred text gone missing.


    Examples
    --------
    .. code-block:: robotframework

        SetConfig   CheckInputValue    True
        SetConfig   CheckInputValue    False
        # One time use:
        TypeText    username           Robot       check=True

    ---
    Parameter: DefaultTimeout

    Set default timeout for QWeb keywords.

    Timeout can be overridden by entering it manually

    Examples
    --------
    .. code-block:: robotframework

        SetConfig   DefaultTimeout    10s
        # One time use:
        VerifyText        Foo          60s

    ---
    Parameter: XHRTimeout

    Set default timeout for XHR (How log we wait page to be loaded).

    Timeout can be overridden by entering it manually

    Examples
    --------
    .. code-block:: robotframework

        SetConfig   XHRTimeout        60

    ---
    Parameter: DefaultDocument

    Switches to default frame automatically.

    If some other frame is used by previous keyword
    we switch back to default after keyword is executed so
    that we are starting to find next locator from html document
    instead of previously used frame.
    Default = True
    Use False only when there is need to use and move
    between frames and page manually for some reason.


    Examples
    --------
    .. code-block:: robotframework

        SetConfig   DefaultDocument    True
        SetConfig   DefaultDocument    False
        SetConfig   DefaultDocument    On
        SetConfig   DefaultDocument    off

    ---
    Parameter: CaseInsensitive

    Set containing_text_match according to selected case sensitivity.

    Default = False
    Note: if containing_text_match has been overwritten manually
    this will return the default value.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig   CaseInsensitive    True
        SetConfig   CaseInsensitive    False

    ---
    Parameter: VerifyAppAccuracy

    Set VerifyApp accuracy. Default is 0.9999. You should not use
    value of 1 because browser rendering will cause false positives.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    VerifyAppAccuracy     0.99999

    ---
    Parameter: WindowSize

    Set window size.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    WindowSize     1920x1080

    ---
    Parameter: InputHandler

    Set input handler.

    Default handler is "selenium" which uses Selenium library's
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

         SetConfig      InputHandler        raw
         SetConfig      InputHandler        selenium

    ---
    Parameter: OffsetCheck

    Element with no offset is considered invisible by default.
    To bypass this check set OffsetCheck to false.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    OffsetCheck     False  #returns also elements that has offset=0
        SetConfig    OffsetCheck     True   #offset is needed (default)
        # One time use:
        ClickItem    Qentinel        offset=False

    ---
    Parameter: Visibility

    If set to false no visibility check is made when searching elements.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    Visibility      False  #returns visible and invisible elements
        SetConfig    Visibility      True   #returns only visible elements(default).
        # One time use:
        ClickItem    Qentinel        visibility=False

    ---
    Parameter: InViewport

    If InViewport is set to true every element outside of current viewport is considered
    invisible. This helps to narrow searching area when there is lots of similar texts/elements
    in dom content. This can be also used to prevent searching functions to match any element
    that is hidden outside of viewport - even if css visibility settings of given element
    says that it's visible.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    InViewport      False  #returns all matching elements(default)
        SetConfig    InViewport      True   #element has to be inside of current viewport
        ClickItem    Qentinel        viewport=False

    ---
    Parameter: SearchMode

    When SearchMode is used, any found web element is highlighted with blue borders
    before the actual execution. This setting is useful especially in debug mode when
    we want to search right kw:s and locators to actual testscript.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    SearchMode      debug  #Highlights element, but won't put action on it
        SetConfig    SearchMode      draw   #Highlights element and then executes kw

    ---
    Parameter: WindowFind

    When WindowFind is used VerifyText is not looking texts for dom, but simulates
    ctrl+f like search to find if text exists.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    WindowFind      True    #Searching text from current viewport
        SetConfig    WindowFind      False   #Searching text from dom(default)

    ---
    Parameter: SearchStrategy Values

    Set search strategy for element search.

    Strategy type is either "all input elements", or "matching input element".

    "all input elements" is a plain xpath that is used to find all elements
    considered as input elements.

    "matching input element" is an xpath with mandatory placeholder "{}" for
    search string. Xpath expression is completed by xpath.format(locator)
    internally and therefore must include placeholder "{}". Used to find elements
    matching with a custom search string. Placeholder can be positional, such as {0}
    and repeated in that case.

    Returns previously used search strategy.


    Examples
    --------
    .. code-block:: robotframework

        SetConfig    ActiveAreaXpath    //input//textarea
        SetConfig    AllInputElements    //input//textarea
        SetConfig    MatchingInputElement    //*[@placeholder="{}"]
        SetConfig    MatchingInputElement    containing input element
        ${previous}= SetConfig    AllInputElements    //input
        SetConfig    AllInputElements    ${previous}

    note: in the above case "containing input element" will use an xpath expression
    such that input elements that contain partial matches are used.

    Parameters
    ----------
    xpath : str
        xpath expression with or without "xpath = "

    Raises
    ------
    ValueError
        Unknown search strategy
    ---
    Parameter: MultipleAnchors

    Normally QWeb requires anchor to be an unique text. If MultipleAnchors is set to False,
    QWeb accepts multiple anchors and selects the first one.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    MultipleAnchors      True    # Accept multiple anchors
        SetConfig    MultipleAnchors      False   # Raise error if anchor is not unique

    ---
    Parameter: ClickToFocus

    Clicks Input element before typing. This is sometimes needed to activate
    target element.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    ClickToFocus         True    # Clicks element before TypeText
        SetConfig    ClickToFocus         False   # Handle TypeText without clicks(default)

    ---
    Parameter: HandleAlerts

    Option for handling alerts boxes, on by default.

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    HandleAlerts       False

    ---
    Parameter: BlindReturn

    Return any value (even empty) from input element without waiting.
    Default = false (Raises QWebValueError if field is empty after timeout).

    Examples
    --------
    .. code-block:: robotframework

        SetConfig    BlindReturn       True
        ${VALUE}     GetInputValue     username
        #Some value must exists inside of given timeout(default):
        SetConfig    BlindReturn       False
        ${VALUE}     GetInputValue     username
        # One time use:
        ${VALUE}     GetInputValue     username     blind=True

    ---
    Parameter: Delay

    Set delay for Paceword.
    This is meant to be used in demo purposes only
    and is not recommended way to control execution flow.
    Default = 0s (No delays before execution).

    Examples
    --------
    .. code-block:: robotframework

        # Wait 0.5 seconds before any Paceword is executed:
        SetConfig    Delay             0.5s
        # One time use - Wait 1s before given Paceword is executed:
        TypeText     username          QRobot   delay=1s

    ---
    Parameter: RetryInterval

    Set default interval for QWeb retry keywords.

    Timeout can be overridden by entering it manually

    Examples
    --------
    .. code-block:: robotframework

        SetConfig   RetryInterval    1s
        # One time use:
        ClickUntil      Foo         button       interval=3

    """
    if not CONFIG.is_value(par):
        raise ValueError("Parameter {} doesn't exist".format(par))
    return CONFIG.set_value(par, val)


def get_config(par=None):
    """Return value of given configuration parameter.

    If no parameter is given the GetConfig returns
    all configurations in a python dictionary of current configuration parameter names and their
    values.

    Examples
    --------
    .. code-block:: robotframework

        ${VAL}    GetConfig    default timeout      # Return default timeout value
        ${VAL}    GetConfig                         # Return all config parameter names and values


    Parameters
    ----------
        par : str
            Setting to be fetched

    """
    if par:
        if not CONFIG.is_value(par):
            raise ValueError("Parameter {} doesn't exist".format(par))
        # Return single configuration value
        current_config = CONFIG.get_value(par)
    else:
        # return whole configuration dictionary
        current_config = CONFIG.get_all_values()
    return current_config


def reset_config(par=None):
    """Reset the value of given parameter to default value.

    If no parameter is given, reset all
    parameters configuration parameters to their defaults.
    Reset also returns the value of the given configuration parameter. If no parameter is given, the
    ResetConfig returns all configurations in a python dictionary with configuration parameter
    name and their values.

    Examples
    --------
    .. code-block:: robotframework

        ${VAL}      ResetConfig    default timeout   # resets single parameter, and returns value
        ${VAL}      ResetConfig                      # Resets all parameters, and returns config

    """
    if par:
        if not CONFIG.is_value(par):
            raise ValueError("Parameter {} doesn't exist".format(par))
        CONFIG.reset_value(par)
        # Return single configuration value
        current_config = CONFIG.get_value(par)
    else:
        CONFIG.reset_value()
        # return whole configuration dictionary
        current_config = CONFIG.get_all_values()
    return current_config
