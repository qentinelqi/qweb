*** Settings ***
Documentation    Tests for input keywords
Library          QWeb
Library          OperatingSystem
Suite Setup      OpenBrowser    http://127.0.0.1:8000/input.html    ${BROWSER}
Suite Teardown   CloseAllBrowsers
Test Timeout     60 seconds

*** Variables ***
${BROWSER}    chrome
${Bar}        1
${foobar}     timeout

*** Test Cases ***
PressKey Paste
    [tags]                  jailed      paste
    CopyText                Test Automation rules
    PressKey                The Brave               {PASTE}
    VerifyInputValue        The Brave               Test Automation rules

Global hotkeys
    [Tags]    PressKey    RESOLUTION_DEPENDENCY
    GoTo           http://127.0.0.1:8000/text.html
    Set Config            WindowSize    1920x1080
    ${scroll_text}=       GetText       Current scroll
    Should Be Equal As Strings    ${scroll_text}                     Current scroll = scroll the window
    PressKey              ${EMPTY}     END
    ${scroll_text}=       GetText       Current scroll               delay=1
    Should Not Be Equal As Strings    ${scroll_text}                 Current scroll = scroll the window
    PressKey              ${EMPTY}     PAGEUP

    ${scroll_text2}=       GetText       Current scroll              delay=1
    Should Not Be Equal As Strings    ${scroll_text}                 ${scroll_text2}