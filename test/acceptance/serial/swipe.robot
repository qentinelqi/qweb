*** Settings ***
Documentation       Test for ClickItem keyword
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}
Test Setup          GoTo    file://${CURDIR}/../../resources/swipe.html
Suite Teardown      CloseBrowser
Test Timeout        60 seconds

*** Variables ***
${BROWSER}    chrome
${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}..${/}resources${/}pics_and_icons${/}icons

*** Test Cases ***
Swipe and verify images
    [Tags]          PROBLEM_IN_WINDOWS	    PROBLEM_IN_FIREFOX  RESOLUTION_DEPENDENCY
    SetConfig       WindowSize   1600x900
    SwipeRight      3
    VerifyIcon      power
    SwipeLeft       4
    VerifyIcon      person
    SwipeDown       2
    VerifyIcon      lock
    SwipeUp         2
    VerifyIcon      person

ScrollTo
    [Tags]            ScrollTo  RESOLUTION_DEPENDENCY
    [Timeout]         20 seconds
    SetConfig         WindowSize   1600x900
    GoTo              file://${CURDIR}/../../resources/text.html
    ScrollTo          Current scroll
    # Verify that we have scrolled (default text "scroll the window" has vanished)
    VerifyNoText      scroll the window
