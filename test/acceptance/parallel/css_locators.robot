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
    GetText
    GetInputValue
    VerifyInputElement

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

GetText With CSS
    ${text}=                    GetText                     css\=button.primary
    Should Be Equal             ${text}                     Save
    ${text}=                    GetText                     css\=li.item               anchor=2
    Should Be Equal             ${text}                     Item 2
    ${text}=                    GetText                     css\=div.card:text-is("Hello world")
    Should Be Equal             ${text}                     Hello world
    ${text}=                    GetText                     css\=#card-hello-world     from_start=5
    Should Be Equal             ${text}                     Hello
    ${text}=                    GetText                     css\=#frame-result
    Should Be Equal             ${text}                     Frame not clicked
    # text and xpath locators work as before
    ${text}=                    GetText                     Hello world
    Should Be Equal             ${text}                     Hello world
    ${text}=                    GetText                     //li[@class\="item"][3]
    Should Be Equal             ${text}                     Item 3

GetText With CSS Ignores Tag
    ${text}=                    GetText                     css\=button.primary         tag=div
    Should Be Equal             ${text}                     Save

GetText With Missing CSS Element Waits For Timeout
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebElementNotFoundError: *css=#missing*
    ...                         GetText                     css\=#missing               timeout=2s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} >= 1.5

VerifyElementText With CSS
    VerifyElementText           css\=button.primary         Save
    VerifyElementText           css\=#card-hello-world      world
    VerifyElementText           css\=#card-hello-world      Hello world                 strict=True
    VerifyElementText           css\=li.item                Item 3                      anchor=3
    VerifyElementText           css\=button.primary         Save                        tag=div
    Run Keyword And Expect Error    QWebValueError: "Hello" != "Hello world"
    ...                         VerifyElementText           css\=#card-hello-world      Hello    strict=True    timeout=1s

VerifyElementText With Invalid CSS Fails At Once
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebInvalidSelectorError: Invalid CSS selector*div[*
    ...                         VerifyElementText           css\=div[                   Save    timeout=10s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} < 5

TypeText With CSS
    TypeText                    css\=input[name\="name"]    Robot
    VerifyInputValue            css\=input[name\="name"]    Robot
    TypeText                    css\=input.name             Nick                        index=2
    VerifyInputValue            css\=input[name\="nickname"]    Nick
    TypeText                    css\=#notes                 Some notes
    VerifyInputValue            css\=#notes                 Some notes
    TypeText                    css\=#editable              Editable text
    VerifyText                  Editable text
    TypeText                    css\=#frame-input           In frame
    VerifyInputValue            css\=#frame-input           In frame
    # label text and xpath work as before
    TypeText                    Name                        By label
    VerifyInputValue            //input[@name\="name"]      By label

TypeText With CSS And CssSelectors Off
    [Setup]                     Run Keywords                Go To    ${BASE_URI}/css_locators.html
    ...                         AND                         SetConfig    CssSelectors    False
    [Teardown]                  SetConfig                   CssSelectors                True
    TypeText                    css\=#notes                 No css selectors
    VerifyInputValue            css\=#notes                 No css selectors

TypeSecret With CSS
    TypeSecret                  css\=input[name\="nickname"]    secret
    ${value}=                   GetInputValue               css\=input[name\="nickname"]
    Should Be Equal             ${value}                    secret

Input Getters And Verifiers With CSS
    ${value}=                   GetInputValue               css\=input.name
    Should Be Equal             ${value}                    Initial
    VerifyInputElement          css\=#notes
    VerifyInputStatus           css\=input[name\="name"]    Enabled
    VerifyInputStatus           css\=#locked                Disabled
    ${elem}=                    GetWebElement               css\=#notes                 element_type=input
    Should Be Equal             ${elem.get_attribute("id")}    notes

PressKey With CSS
    TypeText                    css\=input[name\="name"]    abc
    PressKey                    css\=input[name\="name"]    {BACKSPACE}
    VerifyInputValue            css\=input[name\="name"]    ab

TypeText With Missing CSS Element Waits For Timeout
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebElementNotFoundError: *css=#missing*
    ...                         TypeText                    css\=#missing               text    timeout=2s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} >= 1.5

TypeText With Invalid CSS Fails At Once
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebInvalidSelectorError: Invalid CSS selector*div[*
    ...                         TypeText                    css\=div[                   text    timeout=10s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} < 5

Deprecated Element Type CSS Still Works
    ${elem}=                    GetWebElement               li.item                     element_type=css    index=2
    Should Be Equal             ${elem.text}                Item 2
    ${elem}=                    GetWebElement               css\=li.item                element_type=css    index=3
    Should Be Equal             ${elem.text}                Item 3
    ${value}=                   GetAttribute                button.primary              data-id             element_type=css
    Should Be Equal             ${value}                    save-btn
    VerifyAttribute             button[data-id\="save-btn"]    class                   primary             element_type=css
    &{coords}=                  GetCoordinates              button.primary              element_type=css
    Should Be True              ${coords}[x] > 0
    # same path as css=, so text filters work too
    ${elem}=                    GetWebElement               div.card:text-is("Hello")    element_type=css
    Should Be Equal             ${elem.get_attribute("id")}    card-hello

Deprecated Element Type CSS Fails At Once On Invalid Selector
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebInvalidSelectorError: *
    ...                         GetWebElement               div[                        element_type=css    timeout=10s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} < 5

*** Keywords ***
Invalid Selector Should Fail At Once
    [Arguments]                 ${keyword}
    ${start}=                   Evaluate                    time.time()                 modules=time
    Run Keyword And Expect Error    QWebInvalidSelectorError: Invalid CSS selector*div[*
    ...                         ${keyword}                  css\=div[                   timeout=10s
    ${elapsed}=                 Evaluate                    time.time() - ${start}      modules=time
    Should Be True              ${elapsed} < 5              ${keyword} waited ${elapsed} s
