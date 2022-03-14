*** Settings ***
Documentation                   Tests from element keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 file://${CURDIR}/../resources/text.html                 ${BROWSER}           --headless
Suite Teardown                  CloseBrowser
Test Timeout                    1min

*** Variables ***
${BROWSER}                      chrome

*** Test Cases ***
Hover Element
    HoverText                   Button4                     # make sure we're not hovering already
    VerifyNoText                Hover Link
    HoverElement                //*[@id\="hover_me"]
    VerifyText                  Hover Link

Hover Element by xpath
    HoverText                   Button4                     # make sure we're not hovering already
    VerifyNoText                Hover Link
    HoverElement                xpath\=//*[@id\="hover_me"]
    VerifyText                  Hover Link

Hover Element by WebElement instance
    [Tags]                      WebElement
    HoverText                   Button4                     # make sure we're not hovering already
    VerifyNoText                Hover Link
    ${elem}=                    GetWebElement               hover_me                        element_type=item
    HoverElement                ${elem}
    VerifyText                  Hover Link

Click Element by xpath
    ClickElement                //*[@value\="Button3"]
    VerifyText                  Button3 was clicked

Click Element by xpath 2
    ClickElement                xpath\=//*[@value\="Button4"]
    VerifyText                  Button4 was clicked

Click Element by xpath 3
    Go To                       file://${CURDIR}/../resources/text.html
    Verify No Text              Button4 was clicked
    ClickElement                xpath=//*[@value\="Button4"]
    VerifyText                  Button4 was clicked

Click Element by xpath 4
    Go To                       file://${CURDIR}/../resources/text.html
    Verify No Text              Button4 was clicked
    ClickElement                xpath=//*[@value="Button4"]
    VerifyText                  Button4 was clicked

Click Element by WebElement instance
    [Tags]                      WebElement
    Go To                       file://${CURDIR}/../resources/text.html
    ${elem}=                    GetWebElement               Button4                        element_type=text
    ClickElement                ${elem}
    VerifyText                  Button4 was clicked

IsElementFound
    ${found}=                   IsElement                   //*[@id\="hover_me"]
    Should Be Equal             ${found}                    ${TRUE}

IsElementFound 2
    ${found}=                   IsElement                   xpath\=//*[@id\="hover_me"]
    Should Be Equal             ${found}                    ${TRUE}

IsElementFound 3
    ${found}=                   IsElement                   xpath=//*[@id\="hover_me"]
    Should Be Equal             ${found}                    ${TRUE}

IsElementFound 3
    ${found}=                   IsElement                   xpath=//*[@id="hover_me"]
    Should Be Equal             ${found}                    ${TRUE}

IsElementFoundDelay
    VerifyNoElement             //*[@id\="hide"]
    ClickText                   Show hidden
    ${found}=                   IsElement                   //*[@id\="hide"]            20s
    ShouldBeTrue                ${found}


IsElementFoundDelay attr
    RefreshPage
    VerifyNoElement             hide                        tag=div
    ClickText                   Show hidden
    ${found}=                   IsElement                   hide                        timeout=20s                 tag=div
    ShouldBeTrue                ${found}

IsElementNotFound
    ${found}=                   IsElement                   //*[@id\="no_such_id"]
    Should Be Equal             ${found}                    ${FALSE}

ElementNotFound
    Run Keyword And Expect Error                            QWebElementNotFoundError: Unable to find element for locator*
    ...                         ClickElement                //*[id\='qwerty']           timeout=2

DoubleClick Element
    [Tags]                      PROBLEM_IN_SAFARI
    VerifyNoText                doubleclick test clicked!
    SetConfig                   DoubleClick                 On
    ClickElement                //*[@id\="doubleclick test"]
    VerifyText                  doubleclick test clicked!
    SetConfig                   DoubleClick                 Off

Use attributes without xpath to get element
    RefreshPage
    HoverElement                hover_me                    tag=button
    VerifyText                  Hover Link
    ClickElement                screen                      tag=img
    VerifyText                  Clicks: 1

GetElementCountOK
    [Tags]                      GetElementCount
    Go To                       file://${CURDIR}/../resources/text.html
    ${count}                    GetElementCount             button                      tag=input
    should be equal             ${count}                    ${5}
    ${count}                    GetElementCount             //img
    should be equal             ${count}                    ${1}

GetAttributeOK
    [Tags]                      GetAttribute
    Go To                       file://${CURDIR}/../resources/text.html
    ${attribute}                GetAttribute                SkimClick disable button    id                          element_type=Text
    should be equal             ${attribute}                skimclick
    ${attribute}                GetAttribute                //img                       data-icon
    should be equal             ${attribute}                screen
    ${attribute}                GetAttribute                reset                       value                       element_type=item
    should be equal             ${attribute}                Button4

GetAttributeNOK
    [Tags]                      GetAttribute
    Go To                       file://${CURDIR}/../resources/text.html
    Run Keyword And Expect Error                            QWebElementNotFoundError:*                              GetAttribute         //button[@name\="somethingthatdoesnotexist"]    id    timeout=2
    Run Keyword And Expect Error                            QWebValueError:*            GetAttribute                //button             id                   element_type=Text

VerifyAttributeOK
    [Tags]                      VerifyAttribute
    Go To                       file://${CURDIR}/../resources/text.html
    VerifyAttribute             SkimClick disable button    id                          skimclick                   element_type=Text
    VerifyAttribute             //img                       data-icon                   screen
    VerifyAttribute             reset                       value                       Button4                     element_type=item
    VerifyAttribute             Button                      value                       Button3                     anchor=3             element_type=Text

VerifyAttributeCheckbox
    [Tags]                      VerifyAttribute
    Go To                       file://${CURDIR}/../resources/checkbox.html
    ClickText                   Blue
    VerifyAttribute             //*[@id\="ch_1_1"]          checked                     true
    ClickText                   Blue
    Run Keyword And Expect Error                            QWebValueError:*            VerifyAttribute             //*[@id\="ch_1_1"]                        checked              checked

VerifyAttributeNOK
    [Tags]                      VerifyAttribute
    Go To                       file://${CURDIR}/../resources/text.html
    Run Keyword And Expect Error                            QWebElementNotFoundError:*                              VerifyAttribute      //button[@name\="somethingthatdoesnotexist"]    id    something    timeout=2
    Run Keyword And Expect Error                            QWebValueError:*            VerifyAttribute             //button             value                Button2              element_type=Text