*** Settings ***
Documentation                   Tests for text keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 file://${CURDIR}/../../resources/shadow_dom.html           ${BROWSER}    #--headless
Suite Teardown                  Shadow Teardown
Test Timeout                    60 seconds

Force Tags    windowed

*** Variables ***
${BROWSER}                      chrome

*** Test Cases ***
Basic interactions with Shadow DOM
    [Setup]                     SetConfig                   ShadowDOM                   False
    
    ${error}=                   Run Keyword and Expect Error                            *
    ...                         VerifyText                  Local Target in Shadow DOM                              partial_match=False               timeout=2

    SetConfig                   ShadowDOM                   True
    VerifyText                  Local Target in Shadow DOM
    # partial text should fail without partial_match
    ${error}=                   Run Keyword and Expect Error                            *
    ...                         VerifyText                  Local Target                partial_match=False         timeout=2
    # partial text should found with setting on
    VerifyText                  Local Target                partial_match=True          timeout=2
    VerifyText                  50"                         partial_match=True
    VerifyText                  O'Malley's                  partial_match=True
    VerifyText                  Double quote: 50"           partial_match=False
    VerifyText                  Single quote: O'Malley's    partial_match=False
    VerifyText                  My cat's name is "Bob"      partial_match=True
    VerifyText                  My cat's name is "Bob"      partial_match=False

    TypeText                    What's your name            Robot2                      check=True
    TypeText                    Input2                      Test456

    ClickText                   Click me
    VerifyText                  hidden
    ClickText                   Click me
    VerifyNoText                hidden

    ClickText                   Link
    VerifyText                  Alert popup


Shadow DOM with attributes
    [Setup]                     SetConfig                   ShadowDOM                   True
    GoTo                        file://${CURDIR}/../../resources/shadow_dom.html
    # using attribute values
    VerifyItem                  myButton                    # id
    VerifyItem                  Click this                  # tooltip
    VerifyItem                  Another label               # aria-label
    ${text}=                    GetText                     myButton                    tag=button                  # text
    Should Be Equal As Strings                              Click me                    ${text}
    VerifyItem                  text                        anchor=2                    # numeric anchor
    SetConfig                   HighlightColor              orange
    VerifyItem                  text                        anchor=Local Target in Shadow DOM                       # textual anchor
    Log Screenshot
    ResetConfig                 HighlightColor
    ClickItem                   myButton
    VerifyText                  hidden


Shadow DOM on, normal DOM elements
    [Setup]                     SetConfig                   ShadowDOM                   True
    GoTo                        file://${CURDIR}/../../resources/shadow_dom.html
    # verifying items that are in normal dom
    VerifyText                  In both DOM
    VerifyText                  Level 1
    VerifyText                  Level 2
    VerifyText                  Normal Button
    VerifyItem                  normalbutton
    VerifyText                  Matcha
    VerifyText                  Coffee
    VerifyText                  Water                       anchor=White Tea
    VerifyTextCount             Coffee                      2
    LogScreenshot


VerifyAll & VerifyAny with shadow DOM
    [Setup]                     SetConfig                   ShadowDOM                   False
    GoTo                        file://${CURDIR}/../../resources/shadow_dom.html
    # verify using normal dom only
    ${error}=                   Run Keyword and Expect Error                            *
    ...                         VerifyAll                   In both DOM,Input2          timeout=2
    VerifyAny                   In both DOM,Click me,Input2

    SetConfig                   ShadowDOM                   True
    VerifyAll                   In both DOM,Input2          timeout=2
    VerifyAny                   Click me,In both DOM,Input2


Input keywords with shadow DOM
    [Setup]                     SetConfig                   ShadowDOM                   False
    GoTo                        file://${CURDIR}/../../resources/shadow_dom.html
    # verify inputs using normal dom only
    TypeText                    username                    John Doe                    # in normal/light dom
    ${error}=                   Run Keyword and Expect Error                            *
    ...                         VerifyInputElement          Input2                      timeout=2

    SetConfig                   ShadowDOM                   True
    VerifyInputElement          Input2
    VerifyInputStatus           Input2                      Enabled
    TypeText                    Input2                      Test123
    VerifyInputValue            Input2                      Test123
    VerifyInputValue            username                    John Doe
    ${val}=                     GetInputValue               Input2
    Should Be Equal             ${val}                      Test123

    # text area by text and by attribtue
    TypeText                    Textarea                    Write to textarea
    TypeText                    textarea123                 Modify text in textarea
    TypeText                    textarea456                 Another textarea
    VerifyInputValue            textarea123                 Modify text in textarea
    VerifyInputValue            textarea456                 Another textarea


    # Verify Multiple, both shadow and normal dom
    ${inputs}=                  Create Dictionary           Input2=Test123              What's your name=${EMPTY}
    VerifyInputValues           ${inputs}


Text Counts with shadow DOM
    [Setup]                     SetConfig                   ShadowDOM                   False
    GoTo                        file://${CURDIR}/../../resources/shadow_dom.html
    # verify count using normal dom only
    VerifyTextCount             In both DOM                 1

    # extend search to shadow dom
    SetConfig                   ShadowDOM                   True
    VerifyTextCount             In both DOM                 2
    ${count}=                   GetTextCount                In both DOM
    Should Be Equal As Numbers                              ${count}                    2


Dropdown with shadow DOM
    [Setup]                     SetConfig                   ShadowDOM                   False
    Run Keyword And Expect Error    *    DropDown    Dropdown label    First     timeout=3
    Set Config    ShadowDOM    True
    DropDown    Dropdown label    Second


External site with shadow DOM
    [tags]                      shadow_dom
    [Setup]                     SetConfig                   ShadowDOM                   False
    GoTo                        https://developer.servicenow.com/dev.do
    # dismiss cookie dialog
    ${cookie_dialog}=           IsText                      Required Only               timeout=5
    Run Keyword If              ${cookie_dialog}            ClickText                   Required Only
    Run Keyword If              ${cookie_dialog}            ClickText                   Close

    ${error}=                   Run Keyword and Expect Error                            *
    ...                         VerifyText                  Sign In                     partial_match=False         timeout=3

    SetConfig                   ShadowDOM                   True
    VerifyText                  Sign In                     timeout=3
    ClickText                   Sign In                     timeout=3
    VerifyText                  Remember me                 timeout=20
    LogScreenshot


Chrome shadow DOM
    [Documentation]             Chrome only, verify shadow dom elements in Chrome
    [tags]                      shadow_dom                  PROBLEM_IN_EDGE             PROBLEM_IN_FIREFOX          PROBLEM_IN_SAFARI
    [Setup]                     SetConfig                   ShadowDOM                   True

    SetConfig                   ShadowDOM                   False
    GoTo                        chrome://downloads
    ${error}=                   Run Keyword and Expect Error                            *                           VerifyText           Downloads    timeout=2

    SetConfig                   ShadowDOM                   True
    VerifyText                  Downloads                   timeout=3
    TypeText                    Search downloads            Test
    LogScreenshot


Chrome via aria-label
    [Documentation]             Chrome only, verify shadow dom elements in Chrome using aria-label
    [tags]                      shadow_dom                  PROBLEM_IN_EDGE             PROBLEM_IN_FIREFOX          PROBLEM_IN_SAFARI
    [Setup]                     SetConfig                   ShadowDOM                   False
    GoTo                        chrome://settings/manageProfile
    Run Keyword and Expect Error                            *                           VerifyItem           Cool grey    tag=cr-theme-color    timeout=2
    Run Keyword and Expect Error                            *                           VerifyItem           Cool grey    tag=div               timeout=2
    SetConfig                   ShadowDOM                   True
    
    ${new_format}=              IsItem                      Cool grey                   tag=cr-theme-color       timeout=2  

    IF                          ${new_format}               
        # Chrome 123
        VerifyItem              Cool grey                   tag=cr-theme-color
        ClickItem               Green                       tag=cr-theme-color               
    ELSE
        # Chrome < 123
        VerifyItem              Cool grey                   tag=div
        ClickItem               Midnight blue               tag=div
    END
    
    LogScreenshot

*** Keywords ***
Shadow Teardown
    SetConfig                   ShadowDOM                   False
    CloseBrowser