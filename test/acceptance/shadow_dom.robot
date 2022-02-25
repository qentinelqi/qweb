*** Settings ***
Documentation     Tests for text keywords
Library           QWeb
Suite Setup       OpenBrowser  file://${CURDIR}/../resources/shadow_dom.html  ${BROWSER}   #--HEADLESS
Suite Teardown    CloseBrowser
Test Timeout      1min

*** Variables ***
${BROWSER}         chrome

*** Test Cases ***
Shadow dom with argument
    ${error}=               Run Keyword and Expect Error       *
    ...                    VerifyText      Local Target in Shadow DOM     partial_match=False  timeout=2
    VerifyText             Local Target in Shadow DOM    shadow_dom=True
    TypeText               What's your name              Robot            shadow_dom=True      check=True
    TypeText               Input2                        Test123          shadow_dom=True
    
    ClickText              Click me            shadow_dom=True
    VerifyAlertText        Alert from button
    CloseAlert             Accept
    
    ClickText              Link                shadow_dom=True
    VerifyText             Alert popup


Shadow dom with config
    [Setup]                SetConfig              ShadowDOM                     True
    [Teardown]             SetConfig              ShadowDOM                     False
    
    GoTo                   file://${CURDIR}/../resources/shadow_dom.html
    TypeText               What's your name              Robot2
    TypeText               Input2                        Test456
    
    ClickText              Click me
    VerifyAlertText        Alert from button
    CloseAlert             Accept
    ClickText              Link
    VerifyText             Alert popup


Shadow DOM with attributes
    GoTo                   file://${CURDIR}/../resources/shadow_dom.html
    # using attribute values
    VerifyItem             myButton            shadow_dom=True  # id
    VerifyItem             Click this          shadow_dom=True  # tooltip
    VerifyItem             Another label       shadow_dom=True  # aria-label
    VerifyItem             text                anchor=2    shadow_dom=True  # numeric anchor
    SetConfig              HighlightColor      orange
    VerifyItem             text                anchor=Local Target in Shadow DOM    shadow_dom=True  # textual anchor
    Log Screenshot
    ResetConfig            HighlightColor
    ClickItem              myButton            shadow_dom=True
    VerifyAlertText        Alert from button
    CloseAlert             Accept


VerifyText shadow dom
    [tags]                  shadow_dom
    GoTo                    https://developer.servicenow.com/dev.do
    # dismiss cookie dialog
    ${cookie_dialog}=       IsText      Required Only    timeout=5
    Run Keyword If          ${cookie_dialog}             ClickText     Required Only
     Run Keyword If         ${cookie_dialog}             ClickText     Close

    ${error}=               Run Keyword and Expect Error       *
    ...                     VerifyText      Sign In     partial_match=False  timeout=3
    VerifyText              Sign In         timeout=3                        shadow_dom=True
    Sleep                   3
    ClickText               Sign In         timeout=3                        shadow_dom=True
    TypeText                Email           test@test.com                    shadow_dom=True    timeout=20
    LogScreenshot



Chrome shadow dom
    [Documentation]         Chrome only, verify shadow dom elements in Chrome
    [tags]                  shadow_dom    PROBLEM_IN_WINDOWS    PROBLEM_IN_FIREFOX    PROBLEM_IN_SAFARI
    GoTo                    chrome://downloads
    ${error}=               Run Keyword and Expect Error       *    VerifyText   Downloads   timeout=2
    VerifyText              Downloads        timeout=3                        shadow_dom=True
    TypeText                Search downloads   Test   shadow_dom=True
    LogScreenshot


Chrome via aria-label
    [Documentation]         Chrome only, verify shadow dom elements in Chrome using aria-label
    [tags]                  shadow_dom    PROBLEM_IN_WINDOWS    PROBLEM_IN_FIREFOX    PROBLEM_IN_SAFARI
    GoTo                    chrome://settings/manageProfile
    ${error}=               Run Keyword and Expect Error       *    VerifyText   Cool grey   timeout=2
    VerifyText              Cool grey        timeout=3                        shadow_dom=True
    ClickText               Midnight blue     shadow_dom=True
    LogScreenshot
    
