*** Settings ***
Documentation                   Tests for text keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 ${BASE_URI}/text.html                 ${BROWSER}                  --HEADLESS
Suite Teardown                  CloseBrowser
Test Timeout                    60 seconds

*** Variables ***
${BROWSER}                      chrome
${y_start}                      ${EMPTY}
${y_end}                        ${EMPTY}

*** Test Cases ***
VerifyText needs to be exact match
    [tags]                      fullmatch
    VerifyText                  ipsum dolor
    ${error}=                   Run Keyword and Expect Error                            *
    ...                         VerifyText                  ipsum dolor                 partial_match=False         timeout=1s
    VerifyText                  ipsum dolor
    SetConfig                   PartialMatch                False
    ${error}=                   Run Keyword and Expect Error                            *
    ...                         VerifyText                  ipsum dolor                 timeout=1s
    SetConfig                   PartialMatch                True

VerifyText using WindowFind
    ${error}=                   Run Keyword and Expect Error                            *                           VerifyText
    ...                         //*[text()\='HoverDropdown']                            1s                          window_find=True
    Should Contain              ${error}                    QWebElementNotFoundError: Unable to find
    VerifyText                  HoverDropdown               window_find=True

Verify Text Under One Tag
    VerifyText                  ipsum dolor

Verify Text Under Tag With Subtag
    VerifyText                  Lorem ipsum dolor

Verify Text Many Spaces
    VerifyText                  This sentence contains more than one space between words

Verify Text Not Found Fail
    ${error}=                   Run Keyword and Expect Error                            *                           VerifyText
    ...                         This should not be visible                              1s
    Should Contain              ${error}                    QWebElementNotFoundError: Unable to find

Verify Text Invisible Text Fail
    ${error}=                   Run Keyword and Expect Error                            *                           VerifyText
    ...                         This text should be hidden                              1s
    Should Contain              ${error}                    QWebElementNotFoundError: Unable to find

VerifyText Xpath
    VerifyText                  //*[text()\='HoverDropdown']

VerifyTextBypassJS
    VerifyText                  ipsum dolor                 bypass_js=True

Verify No Text
    VerifyNoText                This should not be visible

Verify No Text Xpath
    VerifyNoText                //*[text()\='qwerty']       0.5s

Verify No Text Invisible Text
    VerifyNoText                This text should be hidden                              2

Verify No Text Text Found Fail
    Run Keyword and Expect Error                            QWebValueError: Page contained the text "Lorem ipsum" after timeout
    ...                         VerifyNoText                Lorem ipsum                 1s

VerifyText Change Default Timeout
    Go To                       ${BASE_URI}/text.html
    VerifyNoText                Delayed hidden text
    SetConfig                   DefaultTimeout              2s
    ClickText                   Show hidden
    ${error}=                   Run Keyword and Expect Error                            *                           VerifyText
    ...                         Delayed hidden text
    Should Contain              ${error}                    QWebElementNotFoundError: Unable to find
    SetConfig                   DefaultTimeout              10s

VerifyTextCountOK
    [Tags]                      VerifyTextCount
    Go To                       ${BASE_URI}/text.html
    VerifyTextCount             Counttextyjku               3                           timeout=1s

VerifyTextCountIsZero
    [Tags]                      VerifyTextCount
    Go To                       ${BASE_URI}/text.html
    VerifyTextCount             Foobarbaz                   0                           timeout=1s

VerifyTextCountIsZeroWithExpected
    [Tags]                      VerifyTextCount
    Go To                       ${BASE_URI}/text.html
    ${error}=                   Run Keyword And Expect Error
    ...                         QWebValueError: Page contained 0 texts instead of 4 after timeout
    ...                         VerifyTextCount             Foobarbaz                   4                           timeout=1s

VerifyTextCountFail
    [Tags]                      VerifyTextCount
    Go To                       ${BASE_URI}/text.html
    ${error}=                   Run Keyword And Expect Error
    ...                         QWebValueError: Page contained 3 texts instead of 4 after timeout
    ...                         VerifyTextCount             Counttextyjku               4                           timeout=1s

VerifyTextCountDelay
    [Tags]                      VerifyTextCount
    Go To                       ${BASE_URI}/text.html
    VerifyTextCount             Counttextyjku               3
    ClickText                   Counttextyjku               anchorcount
    VerifyTextCount             Counttextyjku               4                           timeout=5s

VerifyElementText XPath locator
    [Tags]                      VerifyElementText
    VerifyElementText           //h1                        Hover
    VerifyElementText           //h1                        HoverDropdown               strict=True


VerifyElementText Empty
    [Tags]                      VerifyElementText
    # only has "value" property, no text
    VerifyElementText           //input[@value\="Button3"]                              ${EMPTY}

VerifyElementText use between parameter to get substring
    [Tags]                      VerifyElementText
    VerifyElementText           Hover                       Dropdown                    between=Hover???
    VerifyElementText           ipsum                       dolore                      between=labore et???magna
    VerifyElementText           This sentence               than one space between words 125 603,33                 between=more???
    VerifyElementText           This sentence               This sentence contains      between=???more

VerifyElementText Errors
    [Tags]                      VerifyElementText
    RunKeywordAndExpectError
    ...                         QWebValueError: "Hover" != "HoverDropdown"
    ...                         VerifyElementText           //h1                        Hover                       timeout=3s                  strict=True
    RunKeywordAndExpectError
    ...                         QWebValueError: "foobar" not in "HoverDropdown"
    ...                         VerifyElementText           //h1                        foobar                      timeout=3s

GetTextCountOK
    [Tags]                      GetTextCount
    Go To                       ${BASE_URI}/text.html
    ${count}                    GetTextCount                Counttextyjku
    should be equal             ${count}                    ${3}

GetTextCountisZero
    [Tags]                      GetTextCount
    Go To                       ${BASE_URI}/text.html
    ${count}                    GetTextCount                FooBarBaz                   timeout=2
    should be equal             ${count}                    ${0}

GetText OK
    [Tags]                      GetText
    ${h1}=                      GetText                     //h1                        #HoverDrodDown
    Should Be Equal As Strings                              ${h1}                       HoverDropdown

GetText Element Not Found
    [Tags]                      GetText
    #Element does not exist
    Run Keyword and Expect Error                            QWebElementNotFoundError:*                              GetText                     //h5            timeout=1

GetText Empty
    [Tags]                      GetText
    # only has "value" property, no text
    ${no_text}=                 GetText                     //input[@value\="Button3"]
    Should Be Empty             ${no_text}

GetText Use text as locator1
    [Tags]                      textlocator
    ${text}                     GetText                     Clicks
    ShouldBeEqual               ${text}                     Clicks: 0

GetText Use text as locator2
    [Tags]                      textlocator
    ${text}                     GetText                     contains
    ShouldContain               ${text}                     This sentence contains more than one

GetText Use attribute as locator
    [Tags]                      textlocator
    ${text}                     GetText                     textblock                   tag=p
    ShouldContain               ${text}                     Identifying text

GetText Use between parameter to get substring
    [Tags]                      sub
    ${text}                     GetText                     Hover                       between=Hover???
    ShouldBeEqual               ${text}                     Dropdown
    ${text}                     GetText                     ipsum                       between=labore et???magna
    ShouldBeEqual               ${text}                     dolore
    ${text}                     GetText                     This sentence               between=more???
    ShouldBeEqual               ${text}                     than one space between words 125 603,33
    ${text}                     GetText                     This sentence               between=???more
    ShouldBeEqual               ${text}                     This sentence contains

GetText Use from start parameter to get substring
    [Tags]                      sub                         PROBLEM_IN_SAFARI
    ${text}                     GetText                     dolor                       from_start=5
    ShouldBeEqual               ${text}                     Lorem
    ${text}                     GetText                     dolor                       between=deserunt???         from_start=7
    ShouldBeEqual               ${text}                     mollit

GetText Use from end parameter to get substring
    [Tags]                      sub
    ${text}                     GetText                     dolor                       from_end=8
    ShouldBeEqual               ${text}                     laborum.
    ${text}                     GetText                     dolor                       between=???anim             from_end=7
    ShouldBeEqual               ${text}                     mollit

GetText return float
    [Tags]                      sub
    ${num}                      GetText                     words                       from_end=10                 float=true
    ShouldBeEqual               ${num}                      ${125603.33}
    ${num}                      GetText                     words                       from_end=4                  float=true
    ShouldBeEqual               ${num}                      ${3.33}

GetText return int
    [Tags]                      sub
    ${num}                      GetText                     words                       from_end=10                 int=true
    ShouldBeEqual               ${num}                      ${125603}
    ${num}                      GetText                     words                       from_end=4                  int=true
    ShouldBeEqual               ${num}                      ${3}

IsText True
    [Tags]                      IsText
    ${ret}=                     IsText                      Button4
    Should Be True              ${ret}

IsText Xpath True
    [Tags]                      IsText
    ${ret}=                     IsText                      //*[text()\='HoverDropdown']
    Should Be True              ${ret}

IsText False
    [Tags]                      IsText
    ${ret}=                     IsText                      Irem lopsum
    Should Not Be True          ${ret}

IsText Xpath False
    [Tags]                      IsText
    ${ret}=                     IsText                      //*[text()\='qwerty']
    Should Not Be True          ${ret}

IsText Timeout
    [Tags]                      IsText
    Go To                       ${BASE_URI}/text.html
    VerifyNoText                Delayed hidden text
    ClickText                   Show hidden
    ${ret}=                     IsText                      Delayed hidden text         5s
    Should Be True              ${ret}
    Go To                       ${BASE_URI}/text.html
    VerifyNoText                Delayed hidden text

IsText Timeout False
    [Tags]                      IsText
    Go To                       ${BASE_URI}/text.html
    VerifyNoText                Delayed hidden text
    ClickText                   Show hidden
    ${ret}=                     IsText                      Not there                   0.5s
    Should Not Be True          ${ret}

IsNoText True
    [Tags]                      IsNoText
    ${ret}=                     IsNoText                    qwerty
    Should Be True              ${ret}

IsNoText False
    [Tags]                      IsNoText
    ${ret}=                     IsNoText                    Lorem
    Should Not Be True          ${ret}

IsNoText Xpath False
    [Tags]                      IsText
    ${ret}=                     IsNoText                    //*[text()\='HoverDropdown']
    Should Not Be True          ${ret}

IsNoText Timeout False
    [Tags]                      IsNoText
    ${ret}=                     IsNoText                    Lorem ipsum                 0.5s
    Should Not Be True          ${ret}

Click Text Button Tag
    VerifyNoText                Button1 was clicked
    ClickText                   Button1
    VerifyText                  Button1 was clicked

Click Text Input Type Submit
    VerifyNoText                Button2 was clicked
    ClickText                   Button2
    VerifyText                  Button2 was clicked

Click Text Input Type Button
    VerifyNoText                Button3 was clicked
    ClickText                   Button3
    VerifyText                  Button3 was clicked

Click Text Input Type Reset
    VerifyNoText                Button4 was clicked
    ClickText                   Button4
    VerifyText                  Button4 was clicked

Click Text Text Not Found
    ${message}=                 Set Variable                QWebElementNotFoundError: Unable*
    Run Keyword and Expect Error                            ${message}                  ClickText                   Notext                      1               0.1s

ClickText Invisible Text
    ${message}=                 Set Variable                QWebElementNotFoundError: Unable*
    Run Keyword and Expect Error                            ${message}                  ClickText                   Invisible text              1               timeout=0.1s


Click Button and verify hidden text
    RefreshPage
    VerifyNoText                Delayed hidden text
    ClickText                   Show hidden
    VerifyText                  Delayed hidden text

Click First Button where three with identical value
    ClickText                   Signup                      Anchor 1
    VerifyText                  The first Signup was clicked                            1s

Click Second Button where three with identical value
    RefreshPage
    ClickText                   Signup                      Random text
    VerifyText                  Signup near Random text was clicked                     1s

Click Third Button where three with identical value
    RefreshPage
    ClickText                   Signup                      anchor=Anchor 2
    VerifyText                  The second Signup was clicked                           1s

Multiple Anchors Fail
    [tags]                      dev
    GoTo                        ${BASE_URI}/text.html
    VerifyNoText                The first Signup was clicked
    RunKeywordAndExpectError    QWebValueError*             ClickText                   Signup                      Anchor                      1s
    VerifyNoText                The first Signup was clicked

Multiple Anchors Enabled
    [tags]                      dev
    GoTo                        ${BASE_URI}/text.html
    SetConfig                   MultipleAnchors             True
    VerifyNoText                The first Signup was clicked
    ClickText                   Signup                      Anchor
    VerifyText                  The first Signup was clicked
    [Teardown]                  SetConfig                   MultipleAnchors             False

Hover Text
    [tags]                      hover
    VerifyNoText                Hover Link
    HoverText                   Hover Dropdown
    VerifyText                  Hover Link

Hover Item
    [tags]                      hover
    HoverText                   TextToScroll
    VerifyNoText                Hover Link
    HoverItem                   hover_me                    #Using id as a locator
    VerifyText                  Hover Link
    HoverText                   TextToScroll
    VerifyNoText                Hover Link
    HoverItem                   dropbtn                     #Using classname as a locator
    VerifyText                  Hover Link