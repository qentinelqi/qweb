*** Settings ***
Documentation       Test for ClickItem keyword
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}
Test Setup          GoTo    file://${CURDIR}/../resources/swipe.html
Suite Teardown      CloseBrowser
Test Timeout        1min

*** Variables ***
${BROWSER}    chrome
${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}resources${/}pics_and_icons${/}icons

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

Swipe with starting points and verify images
    [Tags]          swipe   jailed	PROBLEM_IN_FIREFOX  RESOLUTION_DEPENDENCY
    SetCOnfig       WindowSize   1600x900
    SwipeRight      3       Test text 123
    VerifyIcon      power
    SwipeLeft       1    Test text 123
    VerifyText      Test text 123
    SwipeLeft       5    Test text 123
    VerifyIcon      person
    SwipeDown       2       Test text 487
    VerifyIcon      lock
    SwipeUp         1       Test text 487
    VerifyText      Test text 487
    SwipeUp         5       Test text 487
    VerifyIcon      person

ScrollTo
    [Tags]            ScrollTo  RESOLUTION_DEPENDENCY
    SetConfig         WindowSize   1600x900
    GoTo              file://${CURDIR}/../resources/text.html
    ScrollTo          Current scroll
    # Verify that we have scrolled (default text "scroll the window" has vanished)
    VerifyNoText      scroll the window
