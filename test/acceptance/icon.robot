*** Settings ***
Documentation       Tests for icon keywords
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}
Test Setup          GoTo    file://${CURDIR}/../resources/items.html
Suite Teardown      CloseBrowser
Library             Dialogs
Test Timeout        1min

*** Variables ***
${BROWSER}                  chrome
${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}resources${/}pics_and_icons${/}icons

*** Test Cases ***
Click icons
    [Tags]                  PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX
    SetConfig               WindowSize          1920x1080
    Sleep                   2
    ClickIcon               person
    VerifyText              person is my tooltip value!
    ClickIcon               lock
    VerifyText              Lock is my title value!
    ClickIcon               screen
    VerifyText              screen is my data-icon value!

Verify icons
    [Tags]                  PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX
    VerifyIcon              person
    VerifyIcon              power
    VerifyIcon              paperclip
    VerifyIcon              infinity
    VerifyIcon              Lock
    VerifyIcon              screen

Capture icons and verify them
    [Tags]                  PROBLEM_IN_WINDOWS  PROBLEM_IN_FIREFOX
    [Teardown]              RemoveFiles
    CaptureIcon             person     ${BASE_IMAGE_PATH}     capture_icon_1.png
    VerifyIcon              capture_icon_1
    CaptureIcon             power      ${BASE_IMAGE_PATH}     capture_icon_2.png
    VerifyIcon              capture_icon_2
    CaptureIcon             /html/body/table/tbody/tr[1]/td[6]/img      ${BASE_IMAGE_PATH}
    ...                     capture_icon_3.png
    VerifyIcon              capture_icon_3

IsIcon True
    [Tags]                  PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX
    ${result}               isIcon                  paperclip
    Should Be True          ${result}

IsIcon False
    [Tags]                  PROBLEM_IN_WINDOWS
    ${result}               isIcon                  plane
    Should Not Be True      ${result}

WriteText
    [Tags]                  jailed	PROBLEM_IN_FIREFOX
    CloseAllBrowsers
    OpenBrowser             file://${CURDIR}/../resources/input.html    chrome
    ClickIcon               leftright
    WriteText               FooBar
    VerifyInputValue        odjdq               Foobar     selector=id


*** Keywords ***
RemoveFiles
    [Documentation]     Remove files used in CaptureIcon test
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_1.png
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_2.png
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_3.png