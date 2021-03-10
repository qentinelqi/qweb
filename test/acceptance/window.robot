*** Settings ***
Documentation     Tests for window handling
Library           QWeb
Library           Collections
Test Setup        OpenBrowser    about:blank    ${BROWSER}  --headless
Test Teardown     CloseBrowser
Test Timeout      1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Go To
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Should Be Equal    ${driver.current_url}    about:blank
    GoTo                file://${CURDIR}/../resources/window.html
    Should Be Equal    ${driver.title}          Window Acceptance Tests

Open Window
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    OpenWindow
    Length Should Be    ${driver.window_handles}    2

Open Window Changed To New Window
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    GoTo                file://${CURDIR}/../resources/window.html
    OpenWindow
    Should Be Equal    ${driver.current_url}    about:blank

Close Window
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    OpenWindow
    Length Should Be    ${driver.window_handles}    2
    CloseWindow
    Length Should Be    ${driver.window_handles}    1

Switch Window
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    GoTo                file://${CURDIR}/../resources/window.html
    OpenWindow
    Length Should Be    ${driver.window_handles}    2
    Should Be Equal    ${driver.current_url}        about:blank
    SwitchWindow    1
    Should Be Equal    ${driver.title}              Window Acceptance Tests

Switch window, check context
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    GoTo                file://${CURDIR}/../resources/window.html
    OpenWindow
    Length Should Be    ${driver.window_handles}    2
    Should Be Equal     ${driver.current_url}       about:blank
    Close Window
    Should Be Equal    ${driver.title}              Window Acceptance Tests
    VerifyText          Liirum laarum

Switch window, special parameter NEW
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Open New Tab Link Page
    Length Should Be    ${driver.window_handles}    2
    VerifyNoText        Liirum laarum       3       # should not find new window text yet as focus is on parent page
    VerifyText          Parent page
    SwitchWindow        NEW
    VerifyText          Liirum laarum
    VerifyNoText        Parent page         3       # parent page text should not be found as we are in different page
    Close Window                                    # FOcus back in parent page
    VerifyText          Parent page
    #  Multiple windows
    Open Two Windows
    Length Should Be    ${driver.window_handles}    3
    SwitchWindow        3
    CloseWindow
    Length Should Be    ${driver.window_handles}    2
    SwitchWindow        NEW
    VerifyText          Liirum laarum

Switch window, alphanumeric parameters
    ${driver}=    Open New Tab Link Page
    Length Should Be    ${driver.window_handles}    2
    VerifyNoText        Liirum laarum       3       # should not find new window text yet as focus is on parent page
    VerifyText          Parent page
    ${status}=          Run Keyword And Return Status       SwitchWindow        TEST
    Should Be Equal     ${status}           ${False}
    ${status}=          Run Keyword And Return Status       SwitchWindow        NEW
    Should Be Equal     ${status}           ${True}


Switch window, multiple closings, check context
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    GoTo                file://${CURDIR}/../resources/window.html
    OpenWindow
    Length Should Be    ${driver.window_handles}    2
    Should Be Equal     ${driver.current_url}    about:blank
    OpenWindow
    Length Should Be    ${driver.window_handles}    3
    Should Be Equal     ${driver.current_url}    about:blank
    OpenWindow
    Length Should Be    ${driver.window_handles}    4
    Should Be Equal     ${driver.current_url}    about:blank
    Close Window
    Close Window
    Close Window
    Length Should Be    ${driver.window_handles}    1
    Should Be Equal     ${driver.title}             Window Acceptance Tests
    VerifyText          Liirum laarum

Switch window, no other window
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    Run Keyword And Expect Error    QWebDriverError: Tried to select tab with index 2 but there are only 1 tabs open
    ...    Switch Window    2

Switch Window, delay
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    Execute Javascript  setTimeout('window.open()', 3000);
    Length Should Be    ${driver.window_handles}    1
    Switch Window       2                           timeout=8
    Length Should Be    ${driver.window_handles}    2

Close window, no tabs open
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    GoTo                file://${CURDIR}/../resources/window.html
    Close window

Switch window, open multiple, close index
    [Tags]    PROBLEM_IN_SAFARI
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    GoTo                file://${CURDIR}/../resources/window.html
    OpenWindow
    Length Should Be    ${driver.window_handles}    2
    Should Be Equal     ${driver.current_url}    about:blank
    OpenWindow
    Length Should Be    ${driver.window_handles}    3
    GoTO                file://${CURDIR}/../resources/window.html
    Should Be Equal     ${driver.title}             Window Acceptance Tests
    OpenWindow
    Length Should Be    ${driver.window_handles}    4
    Should Be Equal     ${driver.current_url}    about:blank
    SwitchWindow    2
    Close window
    Length Should Be    ${driver.window_handles}    3
    Should Be Equal     ${driver.title}             Window Acceptance Tests

Set Window Size
    [Documentation]     Only setting the size, not verifying anything.
    SetConfig           WindowSize                  1000X800

Maximize Window
    [Documentation]     Tests for MaximizeWindow keyword
    [Tags]              MaximizeWindow
    GoTo                http://howbigismybrowser.com/
    Sleep               2       # wait for browser
    SetConfig           WindowSize                  550X550
    Sleep               2                           # give time for size to change
    LogScreenshot
    ${driver}=          Return Browser
    ${size}             Set Variable   ${driver.get_window_size()}
    ${width} =	        Get From Dictionary	${size}     width
    ${height} =	        Get From Dictionary	${size}     height
    Log                 Window size: ${width}x${height}
    
    MaximizeWindow
    Sleep               2                           # give time for size to change
    LogScreenshot
    ${max_size}             Set Variable   ${driver.get_window_size()}
    ${max_width} =	        Get From Dictionary	${max_size}     width
    ${max_height} =	        Get From Dictionary	${max_size}     height

    Log                     Window size after: ${max_width}x${max_height}

    Should be True          ${max_width} > ${width}
    Should be True          ${max_height} > ${height}

Close Other Windows
    [Tags]    PROBLEM_IN_SAFARI
    [Documentation]     Close other windows
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    GoTo                file://${CURDIR}/../resources/window.html
    VerifyText          Liirum
    Close Others
    OpenWindow
    GoTo                file://${CURDIR}/../resources/text.html
    VerifyText          HoverDropdown
    SwitchWindow        1
    VerifyText          Liirum
    OpenWindow
    GoTo                file://${CURDIR}/../resources/table.html
    VerifyText          Table acceptance
    CloseOthers
    Length Should Be    ${driver.window_handles}    1
    VerifyText          Liirum

Self Closing PopUp
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    GoTo                file://${CURDIR}/../resources/window.html
    Close Others
    ClickText          Open
    SwitchWindow       NEW
    VerifyText         Popup-popup
    ClickText          Close
    SwitchWindow       1
    VerifyText         Liirum

SwitchWindow 0
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    RunKeywordAndExpectError    QWebValueError: SwitchWindow index starts at 1.     SwitchWindow        0


*** Keywords ***
Open New Tab Link Page
    ${driver}=    Evaluate    sys.modules["QWeb.internal.browser"].get_current_browser()     modules=sys
    Length Should Be    ${driver.window_handles}    1
    GoTo                file://${CURDIR}/../resources/newtablink.html
    # Open one extra window
    ClickText           Open new window
    Sleep               3                           # Firefox needs some time
    [Return]    ${driver}

Open Two Windows
    ClickText           Open new window
    ClickText           Open new window
    Sleep               3