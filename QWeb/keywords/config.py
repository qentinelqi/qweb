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
from __future__ import annotations
from typing import Union, Optional, Any
from robot.api.deco import keyword
from QWeb.internal import util
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.search_strategy import SearchStrategies


# pylint: disable=too-many-lines
@keyword(tags=["Config"])
def set_config(par: str, val: Any) -> Any:
    r"""Set configuration parameter to given value. Return previous value.

    Summary of possible configurations and their purpose. More information below.

    +---------------------+-----------------------------------------+----------------+
    | Parameter           | Description                             | Default value  |
    +=====================+=========================================+================+
    | ActiveAreaXpath_    | Set search strategy for element search. |                |
    +---------------------+-----------------------------------------+----------------+
    | AllInputElements_   | Set search strategy for element search. |                |
    +---------------------+-----------------------------------------+----------------+
    | BlindReturn_        | Return value without waiting            |   False        |
    +---------------------+-----------------------------------------+----------------+
    | CaseInsensitive_    | Allow case insensitive search when      | False          |
    |                     | partial match is used                   |                |
    +---------------------+-----------------------------------------+----------------+
    | CheckInputValue_    | Check that typed value is stored        | False          |
    |                     | correctly after TypeText.               |                |
    +---------------------+-----------------------------------------+----------------+
    | ClearKey_           | Set key to be clear previous value when | webdriver's    |
    |                     | text is written to input field (or None)| default clear  |
    +---------------------+-----------------------------------------+----------------+
    | ClickToFocus_       | Sets focus by clicking the field before |   False        |
    |                     | typing.                                 |                |
    +---------------------+-----------------------------------------+----------------+
    | CssSelectors_       | Use CSS selectors for finding elements  | True           |
    +---------------------+-----------------------------------------+----------------+
    | DefaultDocument_    | Automatically switch back to default    | True           |
    |                     | framew after each keyword.              |                |
    +---------------------+-----------------------------------------+----------------+
    | DefaultTimeout_     | How long to wait for element to appear  | 10s            |
    |                     | before failing the case.                |                |
    +---------------------+-----------------------------------------+----------------+
    | Delay_              | Wait time before each keyword           |   0 (no delay) |
    +---------------------+-----------------------------------------+----------------+
    | DoubleClick_        | Perform double-click action in all click|   False        |
    |                     | keywords.                               |                |
    +---------------------+-----------------------------------------+----------------+
    | HandleAlerts_       | Automatically handle alerts.            |   True         |
    +---------------------+-----------------------------------------+----------------+
    | HighlightColor_     | Sets the highlight color to use when    |   blue         |
    |                     | element is highlighted.                 |                |
    +---------------------+-----------------------------------------+----------------+
    | InputHandler_       | Use javascript, selenium or pyautogui   | selenium       |
    |                     | to input text.                          |                |
    +---------------------+-----------------------------------------+----------------+
    | InViewport_         | If set to true every element outside of | False          |
    |                     | current viewport is considered invisible|                |
    |                     | and not returned by default searches    |                |
    +---------------------+-----------------------------------------+----------------+
    | IsModalXPath_       | Set search strategy for element search. |                |
    +---------------------+-----------------------------------------+----------------+
    | LineBreak_          | Set key to send to text fields after    | ue004 (tab key)|
    |                     | typing.                                 |                |
    +---------------------+-----------------------------------------+----------------+
    | LogMatchedIcons_    | Highlights where icon was found on the  |   False        |
    |                     | screen and adds a sceenshot to logs     |                |
    +---------------------+-----------------------------------------+----------------+
    | LogScreenShot_      | Adds screenshot of failure to logs      | True           |
    +---------------------+-----------------------------------------+----------------+
    |MatchingInputElement_| Set search strategy for element search. |                |
    +---------------------+-----------------------------------------+----------------+
    | MultipleAnchors_    | Accept non-unique anchors.              |   False        |
    +---------------------+-----------------------------------------+----------------+
    | OffsetCheck_        | Check element has offset. Element with  | True           |
    |                     | no offset is considered invisible.      |                |
    +---------------------+-----------------------------------------+----------------+
    | OSScreenshots_      | Use operating system functionalities    | False          |
    |                     | instead of selenium to take screenshots |                |
    +---------------------+-----------------------------------------+----------------+
    | PartialMatch_       | Accept partial matches from element     | True           |
    |                     | search functions or require exact match |                |
    +---------------------+-----------------------------------------+----------------+
    | RenderWait_         | Time to wait for dom to stabilize before|   200ms        |
    |                     | interacting (milliseconds).             |                |
    +---------------------+-----------------------------------------+----------------+
    | RetinaDisplay_      | Is current monitor Retina display       |   Automatic    |
    |                     | (True) or not (False)                   |   detection    |
    +---------------------+-----------------------------------------+----------------+
    | RetryInterval_      | Timeout to wait before re-trying in     |   5s           |
    |                     | -Until/-While keywords.                 |                |
    +---------------------+-----------------------------------------+----------------+
    | RunBefore_          | A keyword to be run before every        |   None         |
    |                     | interaction keyword. Useful for example |                |
    |                     | when there is a custom spinner that     |                |
    |                     | should be waited for                    |                |
    +---------------------+-----------------------------------------+----------------+
    | ScreenShotType_     | Log html source, screenshot or both     | screenshot     |
    +---------------------+-----------------------------------------+----------------+
    | SearchDirection_    | Set relative search direction for       | closest        |
    |                     | element search (closest, up, down, left,|                |
    |                     | right, up!, down!, left!, right!)       |                |
    +---------------------+-----------------------------------------+----------------+
    | SearchMode_         | Options for highlighting elements found | draw           |
    |                     | by searches (None, debug, draw).        |                |
    +---------------------+-----------------------------------------+----------------+
    | ShadowDOM_          | Extend element searches to shadow DOM.  |   False        |
    +---------------------+-----------------------------------------+----------------+
    | SpinnerCSS_         | CSS selector for the spinner element to | none           |
    |                     | wait for in default wait function.      |                |
    +---------------------+-----------------------------------------+----------------+
    | StayInCurrentFrame_ | Only search from current frame, do not  |   False        |
    |                     | automatically find elements from all    |                |
    |                     | frames. Useful with \`UseFrame\`.       |                |
    +---------------------+-----------------------------------------+----------------+
    | XHRTimeout_         | Maximum wait for page to be loaded      | 30s            |
    +---------------------+-----------------------------------------+----------------+
    | WaitStrategy_       | Controls which synchronization strategy |                |
    |                     | is used before actions (clicks, typing, | enhanced       |
    |                     | verifications).                         |                |
    |                     | This determines how the framework       |                |
    |                     | decides that the page is "ready".       |                |
    +---------------------+-----------------------------------------+----------------+
    | VerifyAppAccuracy_  | Threshold for needed similarity in      | 0.9999         |
    |                     | VerifyApp keyword.                      |                |
    +---------------------+-----------------------------------------+----------------+
    | Visibility_         | Set if visibility should be checked when| True           |
    |                     | searching for elements.                 |                |
    +---------------------+-----------------------------------------+----------------+
    | WindowFind_         | Simulate CTRL+F to search for elements  | False          |
    |                     | instead of searching from DOM           |                |
    +---------------------+-----------------------------------------+----------------+
    | WindowSize_         | Set the size of browser window          | Full screen    |
    +---------------------+-----------------------------------------+----------------+


    .. _blindreturn:

    ----

    Parameter: BlindReturn
    ----------------------

    Return any value (even empty) from input element without waiting.
    Default = false (Raises QWebValueError if field is empty after timeout).

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    BlindReturn       True
        ${VALUE}     GetInputValue     username
        #Some value must exists inside of given timeout(default):
        SetConfig    BlindReturn       False
        ${VALUE}     GetInputValue     username
        # One time use:
        ${VALUE}     GetInputValue     username     blind=True

    .. _caseinsensitive:

    ----

    Parameter: CaseInsensitive
    --------------------------

    Set containing_text_match according to selected case sensitivity.

    Default = False
    Note: if containing_text_match has been overwritten manually
    this will return the default value.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   CaseInsensitive    True
        SetConfig   CaseInsensitive    False

    .. _checkinputvalue:

    ----

    Parameter: CheckInputValue
    --------------------------

    Check that real value matches to preferred value after TypeText.

    If value is not match we try to re type (three times before fail)
    This is optional feature. Default = false.
    Use with caution on elements where webdriver has tendency to lost focus
    and some part of the preferred text gone missing.


    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   CheckInputValue    True
        SetConfig   CheckInputValue    False
        # One time use:
        TypeText    username           Robot       check=True

    .. _clearkey:

    ----

    Parameter: ClearKey
    -------------------

    Set key to be pressed before text is written to input field.

    By default uses webdrivers clear method to clear element.

    Available values are same as with LineBreak. Some keyboard shortcuts
    also available. Some examples from link below:
    https://turbofuture.com/computers/keyboard-shortcut-keys:

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   ClearKey     None           # Uses clear method (=default)
        SetConfig   ClearKey     {NULL}         # Does nothing
        SetConfig   ClearKey     {CONTROL + A}  # Select all and overwrite
        # One time use:
        TypeText    username    Robot       clear_key={CONTROL + A}

    .. _clicktofocus:

    ----

    Parameter: ClickToFocus
    -----------------------

    Clicks Input element before typing. This is sometimes needed to activate
    target element.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    ClickToFocus         True    # Clicks element before TypeText
        SetConfig    ClickToFocus         False   # Handle TypeText without clicks(default)

    .. _cssselectors:

    ----

    Parameter: CssSelectors
    -----------------------

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
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    CssSelectors       on
        TypeText     MyLocator   Robot
        SetConfig    CssSelectors       off

    .. _defaultdocument:

    ----

    Parameter: DefaultDocument
    --------------------------

    Switches to default frame automatically.

    If some other frame is used by previous keyword
    we switch back to default after keyword is executed so
    that we are starting to find next locator from html document
    instead of previously used frame.
    Default = True
    Use False only when there is need to use and move
    between frames and page manually for some reason.

    Related setting: StayInCurrentFrame_


    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   DefaultDocument    True
        SetConfig   DefaultDocument    False
        SetConfig   DefaultDocument    On
        SetConfig   DefaultDocument    off

    .. _defaulttimeout:

    ----

    Parameter: DefaultTimeout
    -------------------------

    Set default timeout for QWeb keywords.

    Timeout can be overridden by entering it manually

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   DefaultTimeout    10s
        # One time use:
        VerifyText        Foo          60s

    .. _delay:

    ----

    Parameter: Delay
    ----------------

    Set delay for Paceword.
    This is meant to be used in demo purposes only
    and is not recommended way to control execution flow.
    Default = 0s (No delays before execution).

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        # Wait 0.5 seconds before any Paceword is executed:
        SetConfig    Delay             0.5s
        # One time use - Wait 1s before given Paceword is executed:
        TypeText     username          QRobot   delay=1s

    .. _doubleclick:

    ----

    Parameter: DoubleClick
    ----------------------

    Sets double-click the default action for all Click* keywords.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    DoubleClick          True    # All Click keywords perform double-click action
        SetConfig    DoubleClick          False   # Single-click action(default)

    .. _handlealerts:

    ----

    Parameter: HandleAlerts
    -----------------------

    Option for handling alerts boxes, on by default.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    HandleAlerts       False

    .. _highlightcolor:

    ----

    Parameter: HighlightColor
    -------------------------

    Sets the highlight color to use when element is highlighted.

    Accepted colors are:

    * aqua
    * black
    * blue
    * fuchsia
    * green
    * lime
    * navy
    * olive
    * orange
    * purple
    * red
    * teal
    * yellow


    Default = "blue".

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    HighlightColor       olive

    .. _inputhandler:

    ----

    Parameter: InputHandler
    -----------------------

    Set input handler.

    Default handler is "selenium" which uses Selenium library's
    methods clear() and send_keys(). These methods assume that
    the web element is writable (enabled). Inserts tab character
    at the end of text.

    Alternative writers "raw" and "javascript. "raw" uses pyautogui to input text directly
    without checking the web element state. "javascript" uses javascript for input.
    These version are intended to be used when the web page doesn't update input element status
    Selenium compliant way.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

         SetConfig      InputHandler        raw
         SetConfig      InputHandler        selenium

         # Use JavaScript to set the text to input element's value attribute
         SetConfig      InputHandler        javascript

    .. _inviewport:

    ----

    Parameter: InViewport
    ---------------------

    If InViewport is set to true every element outside of current viewport is considered
    invisible. This helps to narrow searching area when there is lots of similar texts/elements
    in dom content. This can be also used to prevent searching functions to match any element
    that is hidden outside of viewport - even if css visibility settings of given element
    says that it's visible.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    InViewport      False  #returns all matching elements(default)
        SetConfig    InViewport      True   #element has to be inside of current viewport
        ClickItem    Qentinel        viewport=False

    .. _linebreak:

    ----

    Parameter: LineBreak
    --------------------

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
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   LineBreak    \ue004    # Tab key
        SetConfig   LineBreak    \ue007    # Enter key
        SetConfig   LineBreak    ${EMPTY}  # Do not send anything

    .. _logmatchedicons:

    ----

    Parameter: LogMatchedIcons
    --------------------------

    When True, highlights where icon was found on the screen and adds a sceenshot
    to logs. Default = False (Screenshots are not added to the logs).

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    LogMatchedIcons       True

    .. _logscreenshot:

    ----

    Parameter: LogScreenshot
    ------------------------

    Enables or disables logging screenshots when keyword fails.
    Default is screenshot (True). False disables screenshots from logs when keyword fails.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    LogScreenshot         False
        SetConfig    LogScreenshot         True

    .. _multipleanchors:

    ----

    Parameter: MultipleAnchors
    --------------------------

    Normally QWeb requires anchor to be an unique text. If MultipleAnchors is set to True,
    QWeb accepts multiple anchors and selects the first one.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    MultipleAnchors      True    # Accept multiple anchors
        SetConfig    MultipleAnchors      False   # Raise error if anchor is not unique

    .. _offsetcheck:

    ----

    Parameter: OffsetCheck
    ----------------------

    Element with no offset is considered invisible by default.
    To bypass this check set OffsetCheck to false.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    OffsetCheck     False  #returns also elements that has offset=0
        SetConfig    OffsetCheck     True   #offset is needed (default)
        # One time use:
        ClickItem    Qentinel        offset=False

    .. _osscreenshots:

    ----

    Parameter: OSScreenshots
    ------------------------

    Defines if screenhots are taken using selenium's or operating system's functionalities.
    Default is selenium screenshot (False).

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    OSScreenshots        True
        SetConfig    OSScreenshots        False

    .. _partialmatch:

    ----

    Parameter: PartialMatch
    -----------------------

    Accept partial match (True) from textual element searches
    or require exact match (False)

    Default = True

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   PartialMatch    True
        SetConfig   PartialMatch    False

    .. _renderwait:

    ----

    Parameter: RenderWait
    ---------------------

    Defines the required rendering settle period (in milliseconds) where the page must remain
    unchanged before continuing.
    This acts as a grace period after network activity has finished, ensuring that
    UI rendering, animations, and reflows have completed.

    Internally a cap is applied: the wait will not exceed 1.5 × RenderWait (with an absolute
    maximum of 1500 ms) even if the page never fully settles. This prevents tests from hanging
    indefinitely on pages with continuous background changes
    (e.g. timers, ads, or blinking cursors).

    Default = 200ms (page must be stable for at least 200 milliseconds)

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        # Require 500 ms of rendering stability before continuing
        SetConfig       RenderWait       500ms

        # Interaction waits until page has been stable for 0.5 s,
        # but never more than 750 ms total (1.5 × 500 ms)
        ClickText       Submit
        VerifyText      Submitted

        # Restore default (200 ms)
        SetConfig       RenderWait       200

    .. _retinadisplay:

    ----

    Parameter: RetinaDisplay
    ------------------------

    Is current monitor Retina display (True) or not (False). Will be automatically
    set based on used monitor, but can be changed for testing purposes if needed.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    RetinaDisplay       False

    .. _retryinterval:

    ----

    Parameter: RetryInterval
    ------------------------

    Set default interval for QWeb retry keywords.

    Timeout can be overridden by entering it manually

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   RetryInterval    1s
        # One time use:
        ClickUntil      Foo         button       interval=3

    .. _runbefore:

    ----

    Parameter: RunBefore
    --------------------

    Set a verificaton keyword to be run before any interaction
    keywords (click*, get_text, dropdown).

    Most common use for this configuration is in applications, that have a custom
    "spinner"/ loading indicator which needs to be waited even if
    page itself is already in ReadyState.

    Any custom robot fw keywords which start with word "Verify" can be used as RunBefore keyword.
    A resource file defining this keyword must be imported prior to usage.


    Supports giving keyword to run and parameters either in python or in robot framework syntax.
    Robot fw syntax needs to be given in a variable due to handling of arguments.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        # Python syntax
        SetConfig  RunBefore   element.verify_no_element('//html[contains(@class, "custom-busy")]')
        ClickText  Foo
        # Waits that custom spinner disappears before running other keywords

        # Robot Framework syntax, needs to be in variable
        ${run_bf}=   SetVariable    VerifyNoText    Loading....     timeout=5
        SetConfig    RunBefore      ${run_bf}
        ClickText    Foo
        # Waits that text "Loading..." disappears before running other keywords

    .. _screenshottype:

    ----

    Parameter: ScreenshotType
    -------------------------

    Defines how screenshot is taken. Default is normal screenshot.
    "html" saves page as html frame in test log. "all" saves both image and html page.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    ScreenshotType        html
        SetConfig    ScreenshotType        screenshot
        SetConfig    ScreenshotType        all

    .. _searchdirection:

    ----

    Parameter: SearchDirection
    --------------------------

    Set search direction for element search.

    Search direction is "closest, "up", "down", "left", "right",
    "up!", "down!", "left!", "right!".
    "Closest" is the default value.

    Elements are searched according to their relative position to anchor.

    With this setting you can choose between two ways of searching:

    - **normal mode**
    - **strict mode** (ending with "!").

    **Normal Mode**: In this mode, you start looking for something starting from a specific point
    or direction you've chosen. If you can't find it there, the search will then try to find
    the closest match, even if it's not exactly in the direction you started from.

    **Strict Mode**: This mode is stricter. You also start searching from a specific direction,
    but the big difference is that if what you're looking for isn't found exactly in that direction,
    the search will fail.
    It won't try to find the next closest thing. The search insists that the item must be found in
    the direction you specified, or not at all.
    It's important to note that this enforced format works only when you're searching for text
    on a page, like when you're using commands to verify text is there (VerifyText)
    or when you want to click on text (ClickText).

    Examples
    ^^^^^^^^

    .. code-block:: robotframework

        *** Test Cases ***
        SearchDirection Example
            # finds input using text "My Locator" on the right of text "Robot"
            SetConfig    SearchDirection       right
            TypeText     MyLocator  Hello  Robot

            # finds input using text "My Locator" above of text "Robot"
            SetConfig    SearchDirection       up
            TypeText     MyLocator  Hello  Robot

            # When using strict mode (!), the test case fails if the locator text is
            # not found in the correct direction from the anchor.
            SetConfig    SearchDirection       left!
            VerifyText   Firstname             anchor=Lastname
            SetConfig    SearchDirection       closest

    .. _searchmode:

    ----

    Parameter: SearchMode
    ---------------------

    When SearchMode is used, any found web element is highlighted with blue borders
    before the actual execution. This setting is useful especially in debug mode when
    we want to search right kw:s and locators to actual testscript.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    SearchMode      debug  #Highlights element, but won't put action on it
        SetConfig    SearchMode      draw   #Highlights element and then executes kw (default)
        SetConfig    SearchMode      None   #Turns off highlighting element

    .. _shadowdom:

    ----

    Parameter: ShadowDOM
    --------------------

    Extends element search to open shadow roots / shadow DOM.
    Elments under shadow dom are not reachable by normal means, so setting
    this configuration to True also changes how elements are searched.
    This basically means that some attributes given to keywords can be ignored
    and other search strategies are overridden.

    It's best to use this setting only in specific situations where shadow dom
    elements need to be verified or interacted with.

    Default = False (Elements are only searched from the light / normal dom).

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig       ShadowDOM       True
        # Do things related to shadow dom elements
        VerifyText      This is under shadow root
        ClickText       As is this
        SetConfig       ShadowDOM       False


    .. _spinnercss:

    ----

    Parameter: SpinnerCSS
    -----------------------------

    Defines a comma-separated list of CSS selectors used to detect loading indicators
    (spinners, overlays, progress bars).
    If any element matching these selectors is found and visible, keywords
    will wait until they disappear before continuing.

    This setting is useful when testing applications that show spinners during background
    activity (e.g. Salesforce Lightning, Angular, React apps). If left unset, spinner checks
    are skipped entirely, so waiting relies only on network idle and DOM quiet signals.

    Default = None (spinner checks are not performed).

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    SpinnerCSS   lightning-spinner,.slds-spinner:not(.slds-hide),[aria-busy="true"]


    .. _stayincurrentframe:

    ----

    Parameter: StayInCurrentFrame
    -----------------------------

    Disables default automatic frame traverse when searching elements.

    Use True only when there is need to use a specific frame and
    find elements from that specific frame only.

    Default = False (Automatic frame traverse in on).

    Related setting: DefaultDocument_

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        UseFrame               //iframe
        SetConfig              StayInCurrentFrame   True
        # Sets focus to first nested frame in current frame
        UseFrame               //iframe

    .. _xhrtimeout:

    ----

    Parameter: XHRTimeout
    ---------------------

    Set default timeout for XHR (How log we wait page to be loaded).

    Timeout can be overridden by entering it manually

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig   XHRTimeout        60

    .. _waitstrategy:

    ----

    Parameter: WaitStrategy
    -----------------------

    Controls which synchronization strategy is used before actions (clicks, typing, verifications).
    This determines how the framework decides that the page is "ready".

    Two strategies are available:

    Enhanced (default)
    ^^^^^^^^^^^^^^^^^^
    Uses multiple signals to detect readiness:

    - document.readyState === "complete"
    - No active network requests (patched fetch + XMLHttpRequest, and jQuery.active if available)
    - No visible spinners (if **SpinnerCSS** is configured)
    - DOM has been stable for a configured quiet period (**RenderWait**)

    This mode is suitable for modern single-page applications
    (e.g. Salesforce Lightning, React, Angular), where activity is not tracked by jQuery alone.

    Legacy
    ^^^^^^
    Uses the old jQuery-based waiter:

    - document.readyState === "complete"
    - Optionally injects jQuery if not present
    - Waits until jQuery.active === 0 (no active jQuery AJAX requests)

    Notes:

    - In both strategies the maximum wait time is controlled by the **XHR_TIMEOUT** setting.
      If this timeout expires, the wait ends and execution continues
    - Either strategy can be overridden entirely by calling the SetWaitFunction keyword or function
      and providing your own custom wait implementation.


    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        # Use default (enhanced) waiter
        ClickText       Save
        VerifyText      Saved Successfully

        # Explicitly force legacy waiter
        SetConfig       WaitStrategy    legacy
        ClickText       Save
        VerifyText      Saved Successfully

        # Restore enhanced waiter
        SetConfig       WaitStrategy    enhanced

    .. _verifyappaccuracy:

    ----

    Parameter: VerifyAppAccuracy
    ----------------------------

    Set VerifyApp accuracy. Default is 0.9999. You should not use
    value of 1 because browser rendering will cause false positives.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    VerifyAppAccuracy     0.99999

    .. _windowsize:

    ----

    Parameter: WindowSize
    ---------------------

    Set window size.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    WindowSize     1920x1080

    .. _visibility:

    ----

    Parameter: Visibility
    ---------------------

    If set to false no visibility check is made when searching elements.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    Visibility      False  #returns visible and invisible elements
        SetConfig    Visibility      True   #returns only visible elements(default).
        # One time use:
        ClickItem    Qentinel        visibility=False

    .. _windowfind:

    ----

    Parameter: WindowFind
    ---------------------

    When WindowFind is used VerifyText is not looking texts for dom, but simulates
    ctrl+f like search to find if text exists.

    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    WindowFind      True    #Searching text from current viewport
        SetConfig    WindowFind      False   #Searching text from dom(default)

    .. _activeareaxpath:
    .. _allinputelements:
    .. _ismodalxpath:
    .. _matchinginputelement:

    ----

    Parameter: SearchStrategy Values
    --------------------------------

    Set search strategy for element search.

    Strategy type is either "all input elements", or "matching input element".

    "all input elements" is a plain xpath that is used to find all elements
    considered as input elements.

    "matching input element" is an xpath with mandatory placeholder "{}" for
    search string. Xpath expression is completed by xpath.format(locator)
    internally and therefore must include placeholder "{}". Used to find elements
    matching with a custom search string. Placeholder can be positional, such as {0}
    and repeated in that case.

    If **IsModalXPath** is set to something else than //body, then text based element
    search only considers elements which have the given xpath as ancestor, if
    IsModalXpath exists / is open. This is meant for applications that have modal
    dialogs but do not set elements below the dialog hidden in other means.

    Returns previously used search strategy.


    Examples
    ^^^^^^^^
    .. code-block:: robotframework

        SetConfig    ActiveAreaXpath    //input//textarea
        SetConfig    AllInputElements    //input//textarea
        SetConfig    MatchingInputElement    //*[@placeholder="{}"]
        SetConfig    MatchingInputElement    containing input element
        ${previous}= SetConfig    AllInputElements    //input
        SetConfig    AllInputElements    ${previous}
        SetConfig    IsModalXPath       //div[contains(@class, 'modal-container')]

    note: in the above case "containing input element" will use an xpath expression
    such that input elements that contain partial matches are used.

    Parameters
    ----------
    xpath : str
        xpath expression with or without "xpath = "

    Raises
    ------
    ValueError: Unknown search strategy

    ---

    Related keywords
    ----------------
    \`GetConfig\`, \`ResetConfig\`

    """
    if not CONFIG.is_value(par):
        raise ValueError("Parameter {} doesn't exist".format(par))

    # Handle case insensitivity separately
    if par.lower() == "caseinsensitive":
        _set_case_insensitivity(val)
    return CONFIG.set_value(par, val)


@keyword(tags=("Config", "Getters"))
def get_config(par: Optional[str] = None) -> Union[dict[str, Any], Any]:
    r"""Return value of given configuration parameter.

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

    Related keywords
    ----------------
    \`ResetConfig\`, \`SetConfig\`

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


@keyword(tags=["Config"])
def reset_config(par: Optional[str] = None) -> Union[dict[str, Any], Any]:
    r"""Reset the value of given parameter to default value.

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

    Related keywords
    ----------------
    \`GetConfig\`, \`SetConfig\`

    """
    if par:
        if not CONFIG.is_value(par):
            raise ValueError("Parameter {} doesn't exist".format(par))
        CONFIG.reset_value(par)
        # if case insensitive was reset, reset xpath
        if par.lower() == "caseinsensitive":
            CONFIG.reset_value("ContainingTextMatch")
        # Return single configuration value
        current_config = CONFIG.get_value(par)
    else:
        CONFIG.reset_value()
        # return whole configuration dictionary
        current_config = CONFIG.get_all_values()
    return current_config


def _set_case_insensitivity(val: str) -> None:
    check = util.par2bool(val)

    if check:
        CONFIG.set_value(
            "ContainingTextMatch", SearchStrategies.CONTAINING_TEXT_MATCH_CASE_INSENSITIVE
        )
    else:
        CONFIG.set_value(
            "ContainingTextMatch", SearchStrategies.CONTAINING_TEXT_MATCH_CASE_SENSITIVE
        )
