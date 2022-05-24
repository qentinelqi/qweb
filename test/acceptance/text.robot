*** Settings ***
Documentation     Tests for text keywords
Library           QWeb
Suite Setup       OpenBrowser  file://${CURDIR}/../resources/text.html  ${BROWSER}   --HEADLESS
Suite Teardown    CloseBrowser
Test Timeout      20 seconds

*** Variables ***
${BROWSER}         chrome
${y_start}         ${EMPTY}
${y_end}           ${EMPTY}

*** Test Cases ***
VerifyText needs to be exact match
    [tags]                  fullmatch
    VerifyText              ipsum dolor
    ${error}=               Run Keyword and Expect Error       *
    ...                     VerifyText      ipsum dolor     partial_match=False  timeout=1s
    VerifyText              ipsum dolor
    SetConfig               PartialMatch    False
    ${error}=               Run Keyword and Expect Error       *
    ...                     VerifyText      ipsum dolor     timeout=1s
    SetConfig               PartialMatch    True

VerifyText using WindowFind
    ${error}=               Run Keyword and Expect Error       *            VerifyText
    ...                     //*[text()\='HoverDropdown']   1s   window_find=True
    Should Contain          ${error}                QWebElementNotFoundError: Unable to find
    VerifyText              HoverDropdown           window_find=True

Verify Text Under One Tag
    VerifyText              ipsum dolor

Verify Text Under Tag With Subtag
    VerifyText              Lorem ipsum dolor

Verify Text Many Spaces
    VerifyText              This sentence contains more than one space between words

Verify Text Not Found Fail
    ${error}=               Run Keyword and Expect Error       *            VerifyText
    ...                     This should not be visible   1s
    Should Contain          ${error}                QWebElementNotFoundError: Unable to find

Verify Text Invisible Text Fail
    ${error}=               Run Keyword and Expect Error       *            VerifyText
    ...                     This text should be hidden   1s
    Should Contain          ${error}                QWebElementNotFoundError: Unable to find

VerifyText Xpath
    VerifyText              //*[text()\='HoverDropdown']

VerifyTextBypassJS
    VerifyText              ipsum dolor                        bypass_js=True

Verify No Text
    VerifyNoText            This should not be visible

Verify No Text Xpath
    VerifyNoText            //*[text()\='qwerty']            0.5s

Verify No Text Invisible Text
    VerifyNoText            This text should be hidden      2

Verify No Text Text Found Fail
    Run Keyword and Expect Error       QWebValueError: Page contained the text "Lorem ipsum" after timeout
    ...   VerifyNoText       Lorem ipsum   1s

VerifyText Change Default Timeout
    Go To                   file://${CURDIR}/../resources/text.html
    VerifyNoText            Delayed hidden text
    SetConfig               DefaultTimeout          2s
    ClickText               Show hidden
    ${error}=               Run Keyword and Expect Error       *            VerifyText
    ...                     Delayed hidden text
    Should Contain          ${error}                QWebElementNotFoundError: Unable to find
    SetConfig               DefaultTimeout          10s

VerifyTextCountOK
    [Tags]                  VerifyTextCount
    Go To                   file://${CURDIR}/../resources/text.html
    VerifyTextCount         Counttextyjku    3    timeout=1s

VerifyTextCountIsZero
    [Tags]                  VerifyTextCount
    Go To                   file://${CURDIR}/../resources/text.html
    VerifyTextCount         Foobarbaz    0    timeout=1s

VerifyTextCountIsZeroWithExpected
    [Tags]                  VerifyTextCount
    Go To                   file://${CURDIR}/../resources/text.html
    ${error}=               Run Keyword And Expect Error
    ...                     QWebValueError: Page contained 0 texts instead of 4 after timeout
    ...                     VerifyTextCount         Foobarbaz    4    timeout=1s

VerifyTextCountFail
    [Tags]                  VerifyTextCount
    Go To                   file://${CURDIR}/../resources/text.html
    ${error}=               Run Keyword And Expect Error
    ...                     QWebValueError: Page contained 3 texts instead of 4 after timeout
    ...                     VerifyTextCount         Counttextyjku    4   timeout=1s

VerifyTextCountDelay
    [Tags]                  VerifyTextCount
    [Timeout]               30 seconds
    Go To                   file://${CURDIR}/../resources/text.html
    VerifyTextCount         Counttextyjku    3
    ClickText               Counttextyjku    anchorcount
    VerifyTextCount         Counttextyjku    4    timeout=5s

VerifyElementText XPath locator
    [Tags]                  VerifyElementText
    VerifyElementText       //h1      Hover
    VerifyElementText       //h1      HoverDropdown     strict=True


VerifyElementText Empty
    [Tags]                  VerifyElementText
    # only has "value" property, no text
    VerifyElementText       //input[@value\="Button3"]    ${EMPTY}

VerifyElementText use between parameter to get substring
    [Tags]                VerifyElementText
    VerifyElementText     Hover    Dropdown   between=Hover???
    VerifyElementText     ipsum    dolore     between=labore et???magna
    VerifyElementText     This sentence   than one space between words 125 603,33   between=more???
    VerifyElementText     This sentence   This sentence contains     between=???more

VerifyElementText Errors
    [Tags]                  VerifyElementText
    RunKeywordAndExpectError
    ...          QWebValueError: "Hover" != "HoverDropdown"
    ...          VerifyElementText    //h1    Hover    timeout=3s   strict=True
    RunKeywordAndExpectError
    ...          QWebValueError: "foobar" not in "HoverDropdown"
    ...          VerifyElementText    //h1    foobar   timeout=3s

GetTextCountOK
    [Tags]                  GetTextCount
    Go To                   file://${CURDIR}/../resources/text.html
    ${count}                GetTextCount         Counttextyjku
    should be equal         ${count}    ${3}

GetTextCountisZero
    [Tags]                  GetTextCount
    Go To                   file://${CURDIR}/../resources/text.html
    ${count}                GetTextCount         FooBarBaz  timeout=2
    should be equal         ${count}    ${0}

GetText OK
    [Tags]                  GetText
    ${h1}=                  GetText                 //h1                    #HoverDrodDown
    Should Be Equal As Strings   ${h1}              HoverDropdown

GetText Element Not Found
    [Tags]                  GetText
   #Element does not exist
    Run Keyword and Expect Error       QWebElementNotFoundError:*   GetText   //h5  timeout=1

GetText Empty
    [Tags]                  GetText
    # only has "value" property, no text
    ${no_text}=             GetText                 //input[@value\="Button3"]
    Should Be Empty         ${no_text}

GetText Use text as locator1
    [Tags]                  textlocator
    ${text}                 GetText                 Clicks
    ShouldBeEqual           ${text}                 Clicks: 0

GetText Use text as locator2
    [Tags]                  textlocator
    ${text}                 GetText                 contains
    ShouldContain           ${text}                 This sentence contains more than one

GetText Use attribute as locator
    [Tags]                  textlocator
    ${text}                 GetText                 textblock   tag=p
    ShouldContain           ${text}                 Identifying text

GetText Use between parameter to get substring
    [Tags]                  sub
    ${text}                 GetText                 Hover   between=Hover???
    ShouldBeEqual           ${text}                 Dropdown
    ${text}                 GetText                 ipsum   between=labore et???magna
    ShouldBeEqual           ${text}                 dolore
    ${text}                 GetText                 This sentence   between=more???
    ShouldBeEqual           ${text}                 than one space between words 125 603,33
    ${text}                 GetText                 This sentence   between=???more
    ShouldBeEqual           ${text}                 This sentence contains

GetText Use from start parameter to get substring
    [Tags]                  sub                     PROBLEM_IN_SAFARI
    ${text}                 GetText                 dolor   from_start=5
    ShouldBeEqual           ${text}                 Lorem
    ${text}                 GetText                 dolor   between=deserunt???     from_start=7
    ShouldBeEqual           ${text}                 mollit

GetText Use from end parameter to get substring
    [Tags]                  sub
    ${text}                 GetText                 dolor   from_end=8
    ShouldBeEqual           ${text}                 laborum.
    ${text}                 GetText                 dolor   between=???anim     from_end=7
    ShouldBeEqual           ${text}                 mollit

GetText return float
    [Tags]                  sub
    ${num}                  GetText                 words    from_end=10  float=true
    ShouldBeEqual           ${num}                  ${125603.33}
    ${num}                  GetText                 words    from_end=4   float=true
    ShouldBeEqual           ${num}                  ${3.33}

GetText return int
    [Tags]                  sub
    ${num}                  GetText                 words    from_end=10  int=true
    ShouldBeEqual           ${num}                  ${125603}
    ${num}                  GetText                 words    from_end=4   int=true
    ShouldBeEqual           ${num}                  ${3}

IsText True
    [Tags]                  IsText
    ${ret}=                 IsText                  Button4
    Should Be True          ${ret}

IsText Xpath True
    [Tags]                  IsText
    ${ret}=                 IsText                  //*[text()\='HoverDropdown']
    Should Be True          ${ret}

IsText False
    [Tags]                  IsText
    ${ret}=                 IsText                  Irem lopsum
    Should Not Be True      ${ret}

IsText Xpath False
    [Tags]                  IsText
    ${ret}=                 IsText                  //*[text()\='qwerty']
    Should Not Be True      ${ret}

IsText Timeout
    [Tags]                  IsText
    [Timeout]               30 seconds
    Go To                   file://${CURDIR}/../resources/text.html
    VerifyNoText            Delayed hidden text
    ClickText               Show hidden
    ${ret}=                 IsText                  Delayed hidden text     5s
    Should Be True          ${ret}
    Go To                   file://${CURDIR}/../resources/text.html
    VerifyNoText            Delayed hidden text

IsText Timeout False
    [Tags]                  IsText
    Go To                   file://${CURDIR}/../resources/text.html
    VerifyNoText            Delayed hidden text
    ClickText               Show hidden
    ${ret}=                 IsText                  Not there               0.5s
    Should Not Be True      ${ret}

IsNoText True
    [Tags]                  IsNoText
    ${ret}=                 IsNoText                qwerty
    Should Be True          ${ret}

IsNoText False
    [Tags]                  IsNoText
    ${ret}=                 IsNoText                Lorem
    Should Not Be True      ${ret}

IsNoText Xpath False
    [Tags]                  IsText
    ${ret}=                 IsNoText                //*[text()\='HoverDropdown']
    Should Not Be True      ${ret}

IsNoText Timeout False
    [Tags]                  IsNoText
    ${ret}=                 IsNoText                Lorem ipsum             0.5s
    Should Not Be True      ${ret}

IsNoText Text is out of viewport when viewport check is on
    [Tags]                  jailed
    RefreshPage
    ${ret}=                 IsNoText      TextToScroll
    ShouldNotBeTrue         ${ret}
    ${ret}=                 IsNoText      TextToScroll   viewport=True
    ShouldBeTrue            ${ret}

Click Text Button Tag
    VerifyNoText            Button1 was clicked
    ClickText               Button1
    VerifyText              Button1 was clicked

Click Text Input Type Submit
    VerifyNoText            Button2 was clicked
    ClickText               Button2
    VerifyText              Button2 was clicked

Click Text Input Type Button
    VerifyNoText            Button3 was clicked
    ClickText               Button3
    VerifyText              Button3 was clicked

Click Text Input Type Reset
    VerifyNoText            Button4 was clicked
    ClickText               Button4
    VerifyText              Button4 was clicked

Click Text Text Not Found
    ${message}=    Set Variable    QWebElementNotFoundError: Unable*
    Run Keyword and Expect Error   ${message}    ClickText    Notext   1   0.1s

ClickText Invisible Text
    ${message}=    Set Variable    QWebElementNotFoundError: Unable*
    Run Keyword and Expect Error   ${message}    ClickText      Invisible text   1   timeout=0.1s

ClickText Overlapping
    [tags]                   jailed	PROBLEM_IN_FIREFOX
    ${message}=    Set Variable    QWebDriverError:*
    Run Keyword and Expect Error   ${message}    ClickText     Button6    1    0.1s

Click Button and verify hidden text
    [Timeout]               30 seconds
    RefreshPage
    VerifyNoText            Delayed hidden text
    ClickText               Show hidden
    VerifyText              Delayed hidden text

Click First Button where three with identical value
    ClickText               Signup                  Anchor 1
    VerifyText              The first Signup was clicked    1s

Click Second Button where three with identical value
    RefreshPage
    ClickText               Signup                  Random text
    VerifyText              Signup near Random text was clicked   1s

Click Third Button where three with identical value
    RefreshPage
    ClickText               Signup                  anchor=Anchor 2
    VerifyText              The second Signup was clicked    1s

Multiple Anchors Fail
    [tags]                  dev
    GoTo                            file://${CURDIR}/../resources/text.html
    VerifyNoText                    The first Signup was clicked
    RunKeywordAndExpectError        QWebValueError*   ClickText               Signup                 Anchor   1s
    VerifyNoText                    The first Signup was clicked

Multiple Anchors Enabled
    [tags]                  dev
    GoTo                            file://${CURDIR}/../resources/text.html
    SetConfig                       MultipleAnchors                 True
    VerifyNoText                    The first Signup was clicked
    ClickText                       Signup                          Anchor
    VerifyText                      The first Signup was clicked
    [Teardown]                      SetConfig                       MultipleAnchors            False

Hover Text
    [tags]                  hover
    VerifyNoText            Hover Link
    HoverText               Hover Dropdown
    VerifyText              Hover Link

Hover Item
    [tags]                  hover
    HoverText               TextToScroll
    VerifyNoText            Hover Link
    HoverItem               hover_me    #Using id as a locator
    VerifyText              Hover Link
    HoverText               TextToScroll
    VerifyNoText            Hover Link
    HoverItem               dropbtn     #Using classname as a locator
    VerifyText              Hover Link

ScanClick
    ScanClick               Click me                Clicks: 2              timeout=15s

ScanClick element is item
    RefreshPage
    ScanClick               screen                  Clicks: 2               el_type=item

ScanClick xpath
    RefreshPage
    ScanClick               //*[text()\="Click me"]    Clicks: 2   interval=1  timeout=4s
    ScanClick               Click me                    xpath\=//*[text()\="4"]

ScanClick wrong pre condition
    ${message}=    Set Variable    QWebValueError: Text to appear is already visible.
    Run Keyword and Expect Error   ${message}   ScanClick       Click me    Click me    timeout=2

SkimClick
    RefreshPage
    SkimClick               Button5
    SkimClick               Click me                Clicks: 0

SkimClick element is item
    RefreshPage
    SkimClick               screen                  Clicks: 0               el_type=item

SkimClick wrong pre condition
    ${message}=    Set Variable    QWebValueError: Text to disappear is not visible before click.
    Run Keyword and Expect Error   ${message}   SkimClick       Click me    Qentiro    timeout=2

SkimClick xpath
    RefreshPage
    SkimClick               //*[text()\="Click me"]     Clicks: 0              timeout=15s
    SkimClick               Click me                    xpath\=//*[text()\="1"]

SkimClick slowly disabling button
    RefreshPage
    SkimClick               SkimClick disable button   interval=1
    VerifyText              skim/scan clicked!

SkimClickCorrectErr
    [tags]                  
    [Timeout]               30 seconds
    ${message}=    Set Variable    QWebValueError: Page contained the text "Click me" after timeout*
    Run Keyword and Expect Error   ${message}   SkimClick   HoverDropdown   Click me    timeout=2

ScanClickCorrectErr2
    [tags]                  err
    [Timeout]               30 seconds
    RefreshPage
    ${message}=    Set Variable    QWebElementNotFoundError: Unable to find element for locator skim/scan clicked!*
    Run Keyword and Expect Error   ${message}   ScanClick   HoverDropdown   skim/scan clicked!   timeout=2

ScanClick with disabling button
    [Timeout]               30 seconds
    RefreshPage
    ScanClick               SkimClick disable button    skim/scan clicked!   interval=1

Click While
    [tags]                  whileuntil
    RefreshPage
    ClickWhile               Button5
    ClickWhile               Clicks: 0      Click me

Click While wrong pre condition
    [tags]                  whileuntil
    ${message}=    Set Variable    QWebValueError: Text to disappear is not visible before click.
    Run Keyword and Expect Error   ${message}   ClickWhile    Qentiro   Click me    timeout=2

Click while xpath
    [tags]                  whileuntil
    RefreshPage
    ClickWhile               Clicks: 0      //*[text()\="Click me"]        timeout=15s
    ClickWhile              xpath\=//*[text()\="1"]     Click me

Click Until
    [tags]                   whileuntil
    [Timeout]                30 seconds
    RefreshPage
    ClickUntil               Clicks: 2      Click me     interval 1s  timeout=15s

Click Until xpath
    [tags]                  whileuntil
    [Timeout]               60 seconds
    RefreshPage
    ClickUntil               Clicks: 3      //*[text()\="Click me"]   interval=2  timeout=8s
    ClickUntil               xpath\=//*[text()\="7"]      Click me      interval=1

Click Until wrong pre condition
    [tags]                  whileuntil
    ${message}=    Set Variable    QWebValueError: Text to appear is already*
    Run Keyword and Expect Error   ${message}   Click Until       Click me    Click me    timeout=2

ClickUntil wait element to appear
    [tags]                  whileuntil
    [Timeout]               60 seconds
    RefreshPage
    ClickUntil              hidden-treasure     Show hidden     element=True
    ${message}=    Set Variable    QWebValueError: Element to appear is already*
    Run Keyword and Expect Error   ${message}   Click Until   hidden-treasure  Show hidden   element=True

ClickWhile wait element to disappear
    [tags]                  whileuntil
    [Timeout]               60 seconds
    ClickWhile              hidden-treasure    Hide Text     element=True
    ${message}=    Set Variable    QWebValueError: Element to disappear is not visible*
    Run Keyword and Expect Error   ${message}   ClickWhile   hidden-treasure    Hide Text   element=True

ClickItemWhile
    [Timeout]               60 seconds
    RefreshPage
    ClickItemWhile          Clicks: 0          screen
    ${message}=             Set Variable       QWebValueError: Text to disappear is not visible*
    Run Keyword and Expect Error   ${message}  ClickItemWhile          Clicks: 0          screen

ClickItemUntil
    [Timeout]               60 seconds
    ClickItemUntil          Clicks: 4          screen      interval=2
    ${message}=             Set Variable       QWebValueError: Text to appear*
    Run Keyword and Expect Error   ${message}  ClickItemUntil   Clicks: 4    screen  timeout=2

Hover Text small window
    [Tags]                  PROBLEM_IN_FIREFOX
    # Bug https://qentinel.visualstudio.com/Pace_libraries/_workitems/edit/3364
    SetConfig               WindowSize              576X356
    HoverText               Button1
    VerifyNoText            Hover Link
    HoverText               Hover Dropdown
    VerifyText              Hover Link

ScrollText
    Execute Javascript      return window.pageYOffset   $y_start
    ScrollText              TextToScroll    timeout=3
    Execute Javascript      return window.pageYOffset   $y_end
    Run Keyword If          ${y_end} <= ${y_start}  Fail                    Did not scroll

ClickText quotes
    VerifyElement           //*[text()\=concat('Text with quote character: 40', '"')]
    VerifyElement           //*[text()\=concat('50', '"')]
    ClickElement            //*[text()\='50"']
    VerifyText              fifty inch was clicked

Child and Parents - Click Identifier
    VerifyNoText            textblock clicked!      timeout=2
    ClickText               Identifying text
    VerifyText              textblock clicked!

Child and Parents - Click parent
    [tags]	PROBLEM_IN_FIREFOX
    VerifyNoText            parent clicked!         timeout=2
    ClickText               Identifying text        parent=div
    VerifyText              parent clicked!

Child and Parents - Click child
    VerifyNoText            smiley clicked!         timeout=2
    ClickText               Identifying text        child=span
    VerifyText              smiley clicked!

Child and Parents - JS click Identifier
    VerifyNoText            textblock clicked!      timeout=2
    ClickText               Identifying text        js=True
    VerifyText              textblock clicked!

Child and Parents - JS click parent
    VerifyNoText            parent clicked!         timeout=2
    ClickText               Identifying text        parent=div      js=True
    VerifyText              parent clicked!

Child and Parents - JS click child
    VerifyNoText            smiley clicked!         timeout=2
    ClickText               Identifying text        child=span      JS=True
    VerifyText              smiley clicked!

Doubleclick
    [tags]	PROBLEM_IN_FIREFOX                       Doubleclick
    VerifyNoText            doubleclick test clicked!
    SetConfig               DoubleClick     On
    ClickText               double-click test.
    VerifyText              doubleclick test clicked!
    SetConfig               DoubleClick     Off

Doubleclick with arguments
    [tags]	Doubleclick
    RefreshPage
    VerifyNoText            doubleclick test clicked!    
    ClickText               double-click test.      doubleclick=True
    VerifyText              doubleclick test clicked!

Doubleclick element with arguments
    [tags]	Doubleclick
    RefreshPage
    VerifyNoText            doubleclick test clicked!    
    ClickElement            //*[@id\="doubleclick test"]      doubleclick=True
    VerifyText              doubleclick test clicked!

Doubleclick item with arguments
    [tags]	Doubleclick
    RefreshPage
    VerifyNoText            doubleclick test clicked!    
    ClickItem               doubleclick test      doubleclick=True
    VerifyText              doubleclick test clicked!


VerifyAll String Without Source File With All Found
    [tags]	PROBLEM_IN_FIREFOX      verify_all
    VerifyAll              consectetur   

VerifyAll From File Content With All Found
    [tags]	PROBLEM_IN_FIREFOX      verify_all
    VerifyAll             test5.txt

VerifyAll From File Content With All But One Found
    [tags]	PROBLEM_IN_FIREFOX      verify_all
    Run Keyword and Expect Error   *   VerifyAll      test6.txt

VerifyAll From List All Found
    [tags]	PROBLEM_IN_FIREFOX      verify_all
    ${iddqd}=               Create List     between words 125 603,33    exercitation   qui officia
    ...                     Identifying text    :-)
    Verifyall             ${iddqd}

VerifyAny String Without Source File With All Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    VerifyAny              consectetur

VerifyAny Strings Without Source File With One Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    VerifyAny              captain, consectetur

VerifyAny String Without Source File With None Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
     Run Keyword and Expect Error   QWebValueError: Could not find any of the texts*   VerifyAny   captain

VerifyAny Strings Without Source File With None Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    Run Keyword and Expect Error   QWebValueError: Could not find any of the texts*    VerifyAny    captain, major

VerifyAny From File Content With All But One Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    VerifyAny       test6.txt

VerifyAny From File Content With None Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    Run Keyword and Expect Error   QWebValueError: Could not find any of the texts*    VerifyAny    test7.txt  
     
VerifyAny From List All Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    ${iddqd}=               Create List     between words 125 603,33    exercitation   qui officia
    ...                     Identifying text    :-)
    VerifyAny             ${iddqd}

VerifyAny From List With All But One Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    ${iddqd}=               Create List      exercitation   qui officia     This Should Not Be Found
    VerifyAny            ${iddqd}  

VerifyAny From List With None Found
    [tags]	PROBLEM_IN_FIREFOX      verify_any
    ${iddqd}=               Create List      exercixxxtation   qxxui officiaxxx     This Should Not Be Found
    Run Keyword and Expect Error   *   VerifyAny      ${iddqd}   

WriteText error in headless mode
    [tags]	PROBLEM_IN_FIREFOX    PROBLEM_IN_SAFARI
    [Documentation]     Headless mode is used in suite setup, if that gets changed this test needs
    ...                 to be fixed as well.
    ${error}      Set Variable    QWebEnvironmentError: Running in headless*
    Run Keyword and Expect Error   ${error}    WriteText      Foobar