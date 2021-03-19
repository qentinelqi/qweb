*** Settings ***
Documentation     Tests from element keywords
Library           QWeb
Suite Setup       OpenBrowser    file://${CURDIR}/../resources/text.html    ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Hover Element
    HoverText           Button4                 # make sure we're not hovering already
    VerifyNoText        Hover Link
    HoverElement        //*[@id\="hover_me"]
    VerifyText          Hover Link

Hover Element by xpath
    HoverText           Button4                 # make sure we're not hovering already
    VerifyNoText        Hover Link
    HoverElement        xpath\=//*[@id\="hover_me"]
    VerifyText          Hover Link

Click Element by xpath
    ClickElement        //*[@value\="Button3"]
    VerifyText          Button3 was clicked

Click Element by xpath 2
    ClickElement        xpath\=//*[@value\="Button4"]
    VerifyText          Button4 was clicked

IsElementFound
    ${found}=           IsElement               //*[@id\="hover_me"]
    Should Be Equal     ${found}                ${TRUE}

IsElementFoundDelay
    VerifyNoElement     //*[@id\="hide"]
    ClickText           Show hidden
    ${found}=           IsElement           //*[@id\="hide"]    20s
    ShouldBeTrue        ${found}


IsElementFoundDelay attr
    RefreshPage
    VerifyNoElement     hide                tag=div
    ClickText           Show hidden
    ${found}=           IsElement           hide      timeout=20s   tag=div
    ShouldBeTrue        ${found}

IsElementNotFound
    ${found}=           IsElement               //*[@id\="no_such_id"]
    Should Be Equal     ${found}                ${FALSE}

ElementNotFound
    Run Keyword And Expect Error    QWebElementNotFoundError: Unable to find element for locator*
    ...                             ClickElement    //*[id\='qwerty']   timeout=2

DoubleClick Element
    [Tags]          PROBLEM_IN_SAFARI
    VerifyNoText    doubleclick test clicked!
    SetConfig       DoubleClick     On
    ClickElement    //*[@id\="doubleclick test"]
    VerifyText      doubleclick test clicked!
    SetConfig       DoubleClick     Off

Use attributes without xpath to get element
    RefreshPage
    HoverElement        hover_me      tag=button
    VerifyText          Hover Link
    ClickElement        screen        tag=img
    VerifyText          Clicks: 1

GetElementCountOK
    [Tags]                  GetElementCount
    Go To                   file://${CURDIR}/../resources/text.html
    ${count}                GetElementCount     button    tag=input
    should be equal         ${count}    ${5}
    ${count}                GetElementCount     //img
    should be equal         ${count}    ${1}
