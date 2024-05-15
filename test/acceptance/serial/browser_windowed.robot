*** Settings ***
Documentation     Tests for opening browsers
Library           OperatingSystem
Library           QWeb
Test Setup        Open Browser And Wait A Bit
Test Teardown     Close Browsers And Remove CHROME_ARGS
Test Timeout      90 seconds
Suite Teardown    Close Browsers And Remove CHROME_ARGS
*** Variables ***
${BROWSER}    chrome
${HEADLESS}   ${TRUE}

*** Test Cases ***
Open Browser With Options
    [tags]          PROBLEM_IN_SAFARI
    [Setup]    No Operation
    OpenBrowser    about:blank    ${BROWSER}    no-sandbox, disable-gpu, disable-impl-side-painting

Open Browser with Environment Chromeargs
    [tags]          PROBLEM_IN_SAFARI
    [Setup]    No Operation
    Set Environment Variable     CHROME_ARGS    no-sandbox, disable-gpu, disable-impl-side-painting
    OpenBrowser    about:blank    ${BROWSER}

Open Browser with Options and Environment Chromeargs
    [tags]          PROBLEM_IN_SAFARI
    [Setup]    No Operation
    Set Environment Variable     CHROME_ARGS    no-sandbox, disable-gpu
    OpenBrowser    about:blank    ${BROWSER}    disable-impl-side-painting

Open Browser with experimental args
    [tags]          exp             PROBLEM_IN_SAFARI
    [Setup]    No Operation
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs="download.prompt_for_download": "False", "plugins.always_open_pdf_externally": "True"
    OpenBrowser     about:blank     ${BROWSER}   prefs="download.prompt_for_download": "False"
    OpenBrowser     about:blank     ${BROWSER}   prefs=download.prompt_for_download: False
    Close All Browsers
    OpenBrowser     about:blank     ${BROWSER}   prefs="ps.*,*.p": "1"

Open Browser with options and experimental args
    [tags]          exp             PROBLEM_IN_SAFARI
    [Setup]    No Operation
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs="download.prompt_for_download": "False", "plugins.always_open_pdf_externally": "True"

Open Browser with invalid experimental args string
    [tags]          exp             PROBLEM_IN_SAFARI
    [Setup]    No Operation
    Run Keyword And Expect Error    QWebUnexpectedConditionError: Invalid argument*
    ...     OpenBrowser     about:blank     ${BROWSER}
    ...     prefs=Foobar, "anotherone":"false"

Open Browser with options and verify
    [tags]          exp             PROBLEM_IN_SAFARI    PROBLEM_IN_FIREFOX    PROBLEM_IN_EDGE
    [Documentation]                 Run this only in Chrome
    [Setup]    No Operation
    [Teardown]                      SetConfig            ShadowDOM             Off
    # Suggested format
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs="extensions.ui.developer_mode": "True"
    SetConfig       ShadowDOM       On
    GoTo            chrome://extensions/
    VerifyText      Developer mode
    VerifyText      Load unpacked
    Close All Browsers
    
    # Deprecated format
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs=extensions.ui.developer_mode: True
    SetConfig       ShadowDOM       On
    GoTo            chrome://extensions/
    VerifyText      Developer mode
    VerifyText      Load unpacked
    Close All Browsers

Open Browser in mobile emulation mode
    [tags]          exp             PROBLEM_IN_SAFARI    PROBLEM_IN_FIREFOX
    [Setup]    No Operation
    
    OpenBrowser     http://howbigismybrowser.com/    ${BROWSER}    emulation=385x812
    Log Screenshot
    ExecuteJavascript   return window.innerWidth;   $width
    Log To Console     ${width}   
    Should Be Equal As Integers                     ${width}     385

    CloseBrowser
    OpenBrowser     http://howbigismybrowser.com/     ${BROWSER}    emulation=iPhone SE
    Log Screenshot
    CloseBrowser
    Run Keyword And Expect Error    InvalidArgumentException: *
    ...     OpenBrowser     about:blank     ${BROWSER}    emulation=should not be found

Open Browser with dictionary prefs
    [tags]          exp             PROBLEM_IN_SAFARI
    [Setup]    No Operation
    ${prefsdict}=   Create Dictionary    download.prompt_for_download    False
    ...             plugins.always_open_pdf_externally    True
    OpenBrowser     about:blank     ${BROWSER}
    ...     prefs=${prefsdict}
    [Teardown]     Close Browsers And Remove CHROME_ARGS

*** Keywords ***
Open Browser And Wait A Bit
    IF    $HEADLESS
        OpenBrowser    about:blank    ${BROWSER}    --headless
    ELSE
        OpenBrowser    about:blank    ${BROWSER}
    END
    Sleep    2s

Close Browsers And Remove CHROME_ARGS
    Close All Browsers
    Remove Environment Variable   CHROME_ARGS

    ResetConfig    LogScreenshot
