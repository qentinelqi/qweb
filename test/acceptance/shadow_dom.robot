*** Settings ***
Documentation     Tests for text keywords
Library           QWeb
Suite Setup       Shadow Setup
Suite Teardown    Shadow Teardown
Test Timeout      1min

*** Variables ***
${BROWSER}         chrome

*** Test Cases ***
Shadow dom with config
    [Setup]                SetConfig              ShadowDOM                     False
 
    
    SetConfig              ShadowDOM                     False
    ${error}=               Run Keyword and Expect Error       *
    ...                    VerifyText      Local Target in Shadow DOM     partial_match=False  timeout=2

    SetConfig              ShadowDOM                     True
    VerifyText             Local Target in Shadow DOM 
    TypeText               What's your name              Robot2
    TypeText               Input2                        Test456
    
    ClickText              Click me
    VerifyAlertText        Alert from button
    CloseAlert             Accept
    ClickText              Link
    VerifyText             Alert popup


Shadow DOM with attributes
    [Setup]                SetConfig              ShadowDOM                     True
    GoTo                   file://${CURDIR}/../resources/shadow_dom.html
    # using attribute values
    VerifyItem             myButton            # id
    VerifyItem             Click this          # tooltip
    VerifyItem             Another label       # aria-label
    VerifyItem             text                anchor=2    # numeric anchor
    SetConfig              HighlightColor      orange
    VerifyItem             text                anchor=Local Target in Shadow DOM  # textual anchor
    Log Screenshot
    ResetConfig            HighlightColor
    ClickItem              myButton
    VerifyAlertText        Alert from button
    CloseAlert             Accept


VerifyText shadow dom
    [tags]                  shadow_dom
    [Setup]                 SetConfig              ShadowDOM                     False
    GoTo                    https://developer.servicenow.com/dev.do
    # dismiss cookie dialog
    ${cookie_dialog}=       IsText      Required Only    timeout=5
    Run Keyword If          ${cookie_dialog}             ClickText     Required Only
    Run Keyword If         ${cookie_dialog}              ClickText     Close

    ${error}=               Run Keyword and Expect Error       *
    ...                     VerifyText      Sign In     partial_match=False  timeout=3
    
    SetConfig               ShadowDOM       True
    VerifyText              Sign In         timeout=3
    Sleep                   3
    ClickText               Sign In         timeout=3
    TypeText                Email           test@test.com                    timeout=20
    LogScreenshot



Chrome shadow dom
    [Documentation]         Chrome only, verify shadow dom elements in Chrome
    [tags]                  shadow_dom    PROBLEM_IN_WINDOWS    PROBLEM_IN_FIREFOX    PROBLEM_IN_SAFARI
    [Setup]                 SetConfig              ShadowDOM                     True
    
    SetConfig               ShadowDOM                          False
    GoTo                    chrome://downloads
    ${error}=               Run Keyword and Expect Error       *    VerifyText   Downloads   timeout=2
    
    SetConfig               ShadowDOM                          True
    VerifyText              Downloads        timeout=3
    TypeText                Search downloads   Test
    LogScreenshot


Chrome via aria-label
    [Documentation]         Chrome only, verify shadow dom elements in Chrome using aria-label
    [tags]                  shadow_dom    PROBLEM_IN_WINDOWS    PROBLEM_IN_FIREFOX    PROBLEM_IN_SAFARI
    [Setup]                 SetConfig              ShadowDOM                     False
    GoTo                    chrome://settings/manageProfile
    ${error}=               Run Keyword and Expect Error       *    VerifyText   Cool grey   timeout=2
    
    SetConfig               ShadowDOM        True
    VerifyText              Cool grey        timeout=3
    ClickText               Midnight blue
    LogScreenshot
    
*** Keywords ***
Shadow Setup
    OpenBrowser              file://${CURDIR}/../resources/shadow_dom.html  ${BROWSER}   #--HEADLESS
    SetConfig              ShadowDOM                     True
       

Shadow Teardown
    SetConfig              ShadowDOM                     False
    CloseBrowser