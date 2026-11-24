*** Settings ***
Documentation                   Tests for css= locators in *Element keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 ${BASE_URI}/css_locators.html         ${BROWSER}           --headless
Suite Teardown                  CloseBrowser
Test Setup                      Go To                       ${BASE_URI}/css_locators.html
Test Timeout                    60 seconds

*** Variables ***
${BROWSER}                      chrome

*** Test Cases ***
Click Element With CSS Class Selector
    ClickElement                css\=button.primary
    VerifyText                  Clicked: Save

Click Element With CSS Attribute Selector
    ClickElement                css\=button[data-id\="save-btn"]
    VerifyText                  Clicked: Save

Click Element With CSS Child Selector
    ClickElement                css\=#user-menu > li:nth-child(2)
    VerifyText                  Clicked: Settings

Click Element With CSS And Index
    ClickElement                css\=li.item                index=2
    VerifyText                  Clicked: item 2
    ClickElement                css\=li.item                index=3
    VerifyText                  Clicked: item 3

Click Element With CSS And Whitespace
    ClickElement                css\=${SPACE}button.primary${SPACE}
    VerifyText                  Clicked: Save

Right Click And Hover Element With CSS
    RightClick                  css\=#context
    VerifyText                  Right clicked
    HoverElement                css\=#hover
    VerifyText                  Hovered

Verify Element With CSS
    VerifyElement               css\=input[name\="email"]
    VerifyElement               css\=#user-menu > li:nth-child(2)
    ${found}=                   IsElement                   css\=button.primary
    Should Be True              ${found}
    ${found}=                   IsElement                   css\=#missing
    Should Not Be True          ${found}

Verify No Element With CSS
    VerifyNoElement             css\=#missing
    # hidden element follows the same visibility rules as XPath
    VerifyNoElement             css\=.hidden-el             timeout=1s

Get Element Count With CSS
    ${count}=                   GetElementCount             css\=li.item
    Should Be Equal As Integers    ${count}                 3

Getters With CSS
    ${elem}=                    GetWebElement               css\=li.item                index=2
    Should Be Equal             ${elem.text}                Item 2
    ${elems}=                   GetWebElement               css\=li.item
    Length Should Be            ${elems}                    3
    ${value}=                   GetAttribute                css\=button.primary         data-id
    Should Be Equal             ${value}                    save-btn
    VerifyAttribute             css\=button.primary         data-id                     save-btn
    &{coords}=                  GetCoordinates              css\=button.primary
    Should Be True              ${coords}[x] > 0

Missing CSS Element Waits For Timeout
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebElementNotFoundError: *css=#missing*
    ...                         VerifyElement               css\=#missing               timeout=2s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} >= 1.5

Late CSS Element Is Found Within Timeout
    VerifyElement               css\=#late                  timeout=5s

Invalid CSS Selector Fails At Once
    [Template]                  Invalid Selector Should Fail At Once
    ClickElement
    RightClick
    HoverElement
    VerifyElement
    VerifyNoElement
    IsElement
    GetElementCount
    GetWebElement

Empty CSS Selector Fails At Once
    Run Keyword And Expect Error    QWebInvalidSelectorError: *selector is empty*
    ...                         ClickElement                css\=                       timeout=10s

CSS Element In Frame
    ClickElement                css\=#in-frame
    VerifyText                  Frame clicked

Tag Is Ignored With CSS
    ClickElement                css\=button.primary         tag=div
    VerifyText                  Clicked: Save

Selector Is Ignored With CSS
    ClickElement                css\=button.primary         selector=id
    VerifyText                  Clicked: Save

XPath Still Works
    ClickElement                //button[@class\="secondary"]
    VerifyText                  Clicked: Cancel
    ClickElement                (//li[@class\="item"])[1]
    VerifyText                  Clicked: item 1
    ClickElement                xpath\=//button[@class\="primary"]
    VerifyText                  Clicked: Save
    ClickElement                xpath=//li[@class\="item"][2]
    VerifyText                  Clicked: item 2
    VerifyElement               xpath=//*[@id\="user-menu"]

Has Text Filter Clicks Matching Card
    ClickElement                css\=div.card:has-text("Hello")
    VerifyText                  Clicked card: card-hello
    ClickElement                css\=div.card:has-text("Hello")    index=2
    VerifyText                  Clicked card: card-hello-world

Has Text Is Substring And Text Is Is Exact
    ${count}=                   GetElementCount             css\=div.card:has-text("Hello")
    Should Be Equal As Integers    ${count}                 3
    ${count}=                   GetElementCount             css\=div.card:text-is("Hello")
    Should Be Equal As Integers    ${count}                 1
    ClickElement                css\=div.card:text-is("Hello world")
    VerifyText                  Clicked card: card-hello-world

Innermost Match Wins
    # outer card contains the inner card's text too, but only the inner one is kept
    ${count}=                   GetElementCount             css\=div.card:has-text("Hello nested")
    Should Be Equal As Integers    ${count}                 1
    ClickElement                css\=div.card:has-text("Hello nested")
    VerifyText                  Clicked card: card-inner
    # inner card doesn't contain "Outer", so the outer card is the only match
    # (checked by id: clicking the outer card's center would hit the inner card)
    ${id}=                      GetAttribute                css\=div.card:has-text("Outer")    id
    Should Be Equal             ${id}                       card-outer

Text Filter Normalizes Whitespace
    VerifyElement               css\=div.card:text-is("Multi space text")
    VerifyElement               css\=div.card:has-text("${SPACE}${SPACE}Multi${SPACE}${SPACE}${SPACE}space${SPACE}")

Text Filter With Quotes
    VerifyElement               css\=p.quote:has-text('Say "hi"')
    VerifyElement               css\=p.quote:has-text("Say \\"hi\\"")
    VerifyElement               css\=p.quote:text-is("It's")

Text Filter Is Case Sensitive And Ignores Match Settings
    [Teardown]                  Run Keywords                SetConfig    CaseInsensitive    False
    ...                         AND                         SetConfig    PartialMatch       True
    VerifyNoElement             css\=p.lower:has-text("Hello")
    SetConfig                   CaseInsensitive             True
    VerifyNoElement             css\=p.lower:has-text("Hello")
    SetConfig                   PartialMatch                False
    ${count}=                   GetElementCount             css\=div.card:has-text("Hello")
    Should Be Equal As Integers    ${count}                 3

Text Filter With No Match Waits For Timeout
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebElementNotFoundError: *:has-text("Nope")*
    ...                         VerifyElement               css\=div.card:has-text("Nope")    timeout=2s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} >= 1.5

Misplaced Text Filter Fails At Once
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebInvalidSelectorError: *only allowed at the end*
    ...                         ClickElement                css\=div.card:has-text("Hello") > span    timeout=10s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} < 5

Text Filter In Frame
    ClickElement                css\=button:has-text("In frame")
    VerifyText                  Frame clicked

Text Filter Has No Effect On XPath
    VerifyElement               //div[contains(., "Alpha")][@class\="card"]
    VerifyNoElement             //div[contains(., ':has-text("Alpha")')]

*** Keywords ***
Invalid Selector Should Fail At Once
    [Arguments]                 ${keyword}
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebInvalidSelectorError: Invalid CSS selector*div[*
    ...                         ${keyword}                  css\=div[                   timeout=10s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} < 5              ${keyword} waited ${elapsed} s
