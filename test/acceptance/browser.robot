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

Open Browser With Options
    Close All Browsers
    OpenBrowser    about:blank    ${BROWSER}    no-sandbox, disable-gpu, disable-impl-side-painting
    [Teardown]     CloseAllBrowsers

Open Browser with Environment Chromeargs
    Close All Browsers
    Set Environment Variable     CHROME_ARGS    no-sandbox, disable-gpu, disable-impl-side-painting
    OpenBrowser    about:blank    ${BROWSER}
    [Teardown]     Close Browsers And Remove CHROME_ARGS

Open Browser with Options and Environment Chromeargs
    Close All Browsers
    Set Environment Variable     CHROME_ARGS    no-sandbox, disable-gpu
    OpenBrowser    about:blank    ${BROWSER}    disable-impl-side-painting
    [Teardown]     Close Browsers And Remove CHROME_ARGS

Open Browser with experimental args
    [tags]          exp
    Close All Browsers
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs="download.prompt_for_download": "False", "plugins.always_open_pdf_externally": "True"
    OpenBrowser     about:blank     ${BROWSER}   prefs="download.prompt_for_download": "False"
    OpenBrowser     about:blank     ${BROWSER}   prefs=download.prompt_for_download: False
    Close All Browsers
    OpenBrowser     about:blank     ${BROWSER}   prefs="ps.*,*.p": "1"

Open Browser with options and experimental args
    [tags]          exp
    Close All Browsers
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs="download.prompt_for_download": "False", "plugins.always_open_pdf_externally": "True"

Open Browser with invalid experimental args string
    [tags]          exp
    Run Keyword And Expect Error    QWebUnexpectedConditionError: Invalid argument*
    ...     OpenBrowser     about:blank     ${BROWSER}
    ...     prefs=Foobar, "anotherone":"false"
    Close Browsers And Remove CHROME_ARGS

Open Browser with dictionary prefs
    [tags]          exp
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
