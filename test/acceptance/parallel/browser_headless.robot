*** Settings ***
Documentation     Tests for opening browsers
Library           OperatingSystem
Library           QWeb
Test Setup        Open Browser And Wait A Bit
Suite Teardown    Teardown Actions
Test Timeout      90 seconds

*** Variables ***
${BROWSER}    chrome
${HEADLESS}   ${TRUE}  #toggle this for seeing the browsers in local testing

*** Test Cases ***
Open Browser 1
    CloseBrowser

Open Browser 2
    CloseBrowser

Close All Browsers 1
    CloseAllBrowsers

Close All Browsers 2
    [Tags]          PROBLEM_IN_WINDOWS      PROBLEM_IN_OSX  PROBLEM_IN_SAFARI    PROBLEM_IN_MACOS
    IF    $HEADLESS
        OpenBrowser     about:blank             firefox    --headless    # force another (firefox) browser to open
    ELSE
        OpenBrowser     about:blank             firefox    # force another (firefox) browser to open
    END
    CloseAllBrowsers

Missing webdriver message
    [Tags]        PROBLEM_IN_MACOS
    [Setup]    CloseAllBrowsers
    Run Keyword and Expect Error    NoSuchDriverException*    OpenBrowser    about:blank    safari    --headless

No browser open message
    [Setup]    No Operation
    [Teardown]    CloseAllBrowsers
    ${previous}=    SetConfig               LogScreenshot    False
    Run Keyword and Expect Error    QWebDriverError: No browser open*    GoTo    https://www.qentinel.com
    SetConfig               LogScreenshot    ${previous}

ScrollText
    [Teardown]    CloseAllBrowsers
    GoTo            ${BASE_URI}/input.html
    ScrollText      UpDown

SwitchBrowser
    [Tags]          PROBLEM_IN_WINDOWS    PROBLEM_IN_MACOS
    GoTo            ${BASE_URI}/multielement_text.html
    IF    $HEADLESS
        OpenBrowser     ${BASE_URI}/dropdown.html     chrome    --headless
        OpenBrowser     ${BASE_URI}/frame.html        firefox   --headless
    ELSE
        OpenBrowser     ${BASE_URI}/dropdown.html     chrome
        OpenBrowser     ${BASE_URI}/frame.html        firefox
    END
    VerifyText      Text in frame
    SwitchBrowser   1
    VerifyText      Lorem ipsum dolor sit amet
    SwitchBrowser   2
    VerifyText      Delayed dropdown
    Run Keyword and Expect Error    QWebValueError: *index starts at 1*    SwitchBrowser   0
    Run Keyword and Expect Error    QWebDriverError: *Tried to select browser with index*    SwitchBrowser   7
    Run Keyword and Expect Error    QWebValueError: *is not a digit or NEW*    SwitchBrowser   my_fake_browser

*** Keywords ***
Open Browser And Wait A Bit
    IF    $HEADLESS
        OpenBrowser    about:blank    ${BROWSER}    --headless
    ELSE
        OpenBrowser    about:blank    ${BROWSER}
    END
    Sleep    2s

Teardown Actions
    ResetConfig    OSScreenshots
    ResetConfig    LogScreenshot
    CloseAllBrowsers

