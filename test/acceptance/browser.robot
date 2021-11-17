*** Settings ***
Documentation     Tests for opening browsers
Library           OperatingSystem
Library           QWeb
Test Setup        Open Browser And Wait A Bit
Test Timeout      1min
Suite Teardown    Close All Browsers

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Open Browser 1
    CloseBrowser

Open Browser 2
    CloseBrowser

Close All Browsers 1
    CloseAllBrowsers

Close All Browsers 2
    [Tags]          PROBLEM_IN_WINDOWS      PROBLEM_IN_OSX  PROBLEM_IN_SAFARI
    OpenBrowser     about:blank             firefox         # force another (firefox) browser to open
    [Teardown]      CloseAllBrowsers

No browser open message
    ${previous}=    SetConfig               LogScreenshot    False
    CloseAllBrowsers
    Run Keyword and Expect Error    QWebDriverError: No browser open*    GoTo    https://www.qentinel.com
    SetConfig               LogScreenshot    ${previous}

ScrollText
    GoTo            file://${CURDIR}/../resources/input.html
    ScrollText      UpDown
    [Teardown]      CloseAllBrowsers

SwitchBrowser
    [Tags]          PROBLEM_IN_WINDOWS
    GoTo            file://${CURDIR}/../resources/multielement_text.html
    OpenBrowser     file://${CURDIR}/../resources/dropdown.html     chrome
    OpenBrowser     file://${CURDIR}/../resources/frame.html        firefox
    VerifyText      Text in frame
    SwitchBrowser   1
    VerifyText      Lorem ipsum dolor sit amet
    SwitchBrowser   2
    VerifyText      Delayed dropdown
    Run Keyword and Expect Error    QWebValueError: *index starts at 1*    SwitchBrowser   0
    Run Keyword and Expect Error    QWebDriverError: *Tried to select browser with index*    SwitchBrowser   7
    Run Keyword and Expect Error    QWebValueError: *is not a digit or NEW*    SwitchBrowser   my_fake_browser

    [Teardown]      CloseAllBrowsers

Open Browser With Options
    Close All Browsers
    OpenBrowser    about:blank    ${BROWSER}    no-sandbox, disable-gpu, disable-impl-side-painting
    [Teardown]     CloseAllBrowsers

Open Browser with Environment Chromeargs
    [tags]          PROBLEM_IN_SAFARI
    Close All Browsers
    Set Environment Variable     CHROME_ARGS    no-sandbox, disable-gpu, disable-impl-side-painting
    OpenBrowser    about:blank    ${BROWSER}
    [Teardown]     Close Browsers And Remove CHROME_ARGS

Open Browser with Options and Environment Chromeargs
    [tags]          PROBLEM_IN_SAFARI
    Close All Browsers
    Set Environment Variable     CHROME_ARGS    no-sandbox, disable-gpu
    OpenBrowser    about:blank    ${BROWSER}    disable-impl-side-painting
    [Teardown]     Close Browsers And Remove CHROME_ARGS

Open Browser with experimental args
    [tags]          exp             PROBLEM_IN_SAFARI
    Close All Browsers
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs="download.prompt_for_download": "False", "plugins.always_open_pdf_externally": "True"
    OpenBrowser     about:blank     ${BROWSER}   prefs="download.prompt_for_download": "False"
    OpenBrowser     about:blank     ${BROWSER}   prefs=download.prompt_for_download: False
    Close All Browsers
    OpenBrowser     about:blank     ${BROWSER}   prefs="ps.*,*.p": "1"

Open Browser with options and experimental args
    [tags]          exp             PROBLEM_IN_SAFARI
    Close All Browsers
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs="download.prompt_for_download": "False", "plugins.always_open_pdf_externally": "True"

Open Browser with invalid experimental args string
    [tags]          exp             PROBLEM_IN_SAFARI
    Run Keyword And Expect Error    QWebUnexpectedConditionError: Invalid argument*
    ...     OpenBrowser     about:blank     ${BROWSER}
    ...     prefs=Foobar, "anotherone":"false"
    Close Browsers And Remove CHROME_ARGS

Open Browser with dictionary prefs
    [tags]          exp             PROBLEM_IN_SAFARI
    Close All Browsers
    ${prefsdict}=   Create Dictionary    download.prompt_for_download    False
    ...             plugins.always_open_pdf_externally    True
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs=${prefsdict}
    [Teardown]     Close Browsers And Remove CHROME_ARGS

*** Keywords ***
Open Browser And Wait A Bit
    OpenBrowser    about:blank    ${BROWSER}
    Sleep    2s

Close Browsers And Remove CHROME_ARGS
    Close All Browsers
    Remove Environment Variable   CHROME_ARGS
