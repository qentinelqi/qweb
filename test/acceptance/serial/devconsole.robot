*** Settings ***
Documentation       Tests for devconsole keywords
Library             QWeb
Library             String
Suite Setup         OpenBrowser    about:blank    ${BROWSER}   bidi=True
Test Setup          GoTo    ${BASE_URI}/devconsole.html
Suite Teardown      CloseBrowser
#Test Timeout        60 seconds

*** Variables ***
${BROWSER}                  chrome

*** Test Cases ***
Start console capture and verify messages are captured
    [tags]          PROBLEM_IN_SAFARI
    StartConsoleCapture
    ClickText    Run Logs
    Sleep    1s
    ${msgs}=    GetConsoleMessages
    Log    ${msgs}


Filter by source and level
    [tags]          PROBLEM_IN_SAFARI
    ${warnings}=    GetConsoleMessages    level=warning
    Length Should Be    ${warnings}       1

    ${all}=               GetConsoleMessages
    ${console_all}=       GetConsoleMessages    source=console
    ${console_errors}=    GetConsoleMessages    error    source=console
    ${all_errors}=        GetConsoleMessages    error
    ${js}=                GetConsoleMessages    source=js

    Length Should Be    ${console_all}     7
    Length Should Be    ${console_errors}  2
    Length Should Be    ${js}              2
    Length Should Be    ${all_errors}      4
    Length Should Be    ${all}             9

VerifyNoConsole Errors should raise if errors are found
    [tags]          PROBLEM_IN_SAFARI
    Run Keyword And Expect Error   *Console errors found*    VerifyNoConsoleErrors   

Message contains
    [tags]          PROBLEM_IN_SAFARI
    ${delayed}=    GetConsoleMessages    contains=Delayed
    Should Contain    ${delayed[0]["text"]}    LOG: delayed message (500ms)

Stop console capture and verify that no messages are found
    [tags]          PROBLEM_IN_SAFARI
    StopConsoleCapture
    ${msgs}=    GetConsoleMessages
    Should Be Empty    ${msgs}
    VerifyNoConsoleErrors
