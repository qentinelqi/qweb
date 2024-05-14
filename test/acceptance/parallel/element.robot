*** Settings ***
Documentation                   Tests from element keywords
Library                         QWeb
Library                         OperatingSystem
Suite Setup                     OpenBrowser                 http://127.0.0.1:8000/text.html                 ${BROWSER}           --headless
Suite Teardown                  CloseBrowser
Test Timeout                    60 seconds

*** Variables ***
${BROWSER}                      chrome

*** Test Cases ***
Verify Element
    VerifyElement               //*[@value\="Button2"]

Verify Element with xpath named parameter
    VerifyElement               xpath=//*[@value\="Button2"]
    VerifyElement               xpath=//*[@value="Button2"]

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

Get Webelement Invalid Element Type
    [Tags]                      WebElement
    Run Keyword And Expect Error    QWebValueError*    GetWebElement    hover_me    element_type=invalid

Click Element by xpath
    ClickElement                //*[@value\="Button3"]
    VerifyText                  Button3 was clicked

Click Element by xpath 2
    ClickElement                xpath\=//*[@value\="Button4"]
    VerifyText                  Button4 was clicked

Click Element by xpath 3
    Go To                       http://127.0.0.1:8000/text.html
    Verify No Text              Button4 was clicked
    ClickElement                xpath=//*[@value\="Button4"]
    VerifyText                  Button4 was clicked

Click Element by xpath 4
    Go To                       http://127.0.0.1:8000/text.html
    Verify No Text              Button4 was clicked
    ClickElement                xpath=//*[@value="Button4"]
    VerifyText                  Button4 was clicked

Click Element by xpath and index
    Go To                       http://127.0.0.1:8000/text.html
    Verify No Text              Signup near Random text was clicked
    ClickElement                //input[@value\="Signup"]    index=2
    VerifyText                  Signup near Random text was clicked

Click Element by WebElement instance
    [Tags]                      WebElement
    Go To                       http://127.0.0.1:8000/text.html
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

IsElementFound 4
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
    [Tags]
    VerifyNoText                doubleclick test clicked!
    SetConfig                   DoubleClick                 On
    ClickElement                //*[@id\="doubleclick test"]
    VerifyText                  doubleclick test clicked!
    SetConfig                   DoubleClick                 Off

Use attributes without xpath to get element
    [Tags]
    RefreshPage
    HoverText                   Lorem ipsum
    HoverElement                hover_me                    tag=button
    VerifyText                  Hover Link
    ClickElement                screen                      tag=img
    VerifyText                  Clicks: 1

GetElementCountOK
    [Tags]                      GetElementCount
    Go To                       http://127.0.0.1:8000/text.html
    ${count}                    GetElementCount             button                      tag=input
    should be equal             ${count}                    ${5}
    ${count}                    GetElementCount             //img
    should be equal             ${count}                    ${1}

GetAttributeOK
    [Tags]                      GetAttribute
    Go To                       http://127.0.0.1:8000/text.html
    ${attribute}                GetAttribute                SkimClick disable button    id                          element_type=Text
    should be equal             ${attribute}                skimclick
    ${attribute}                GetAttribute                //img                       data-icon
    should be equal             ${attribute}                screen
    ${attribute}                GetAttribute                reset                       value                       element_type=item
    should be equal             ${attribute}                Button4
    ${attribute}                GetAttribute                input#signup2               value                       element_type=css
    should be equal             ${attribute}                Signup
    ${attribute}                GetAttribute                body > input[type\=button]:nth-child(10)   value        element_type=css
    should be equal             ${attribute}                Hide Text
    # with index using css
    ${attribute}                GetAttribute                input   value        element_type=css    index=5
    should be equal             ${attribute}                Show hidden

GetAttributeNOK
    [Tags]                      GetAttribute
    Go To                       http://127.0.0.1:8000/text.html
    Run Keyword And Expect Error    QWebElementNotFoundError:*    GetAttribute         //button[@name\="somethingthatdoesnotexist"]    id    timeout=2
    Run Keyword And Expect Error    QWebValueError:*              GetAttribute         //button                                        id    timeout=2
    # jailed, Chrome 123
    #Run Keyword And Expect Error    QWebElementNotFoundError:*    GetAttribute         //button                                        id    element_type=css    timeout=2

VerifyAttributeOK
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    VerifyAttribute             SkimClick disable button    id                          skimclick                   element_type=Text
    VerifyAttribute             //img                       data-icon                   screen
    VerifyAttribute             reset                       value                       Button4                     element_type=item
    VerifyAttribute             Button                      value                       Button3                     anchor=3             element_type=Text
    VerifyAttribute             \#signup2                   value                       Signup                      element_type=css
    VerifyAttribute             p a                         id                          clicks                      element_type=css
    VerifyAttribute             p a                         id                          clicks                      element_type=css     operator=\==

VerifyAttributeNotEquals
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    VerifyAttribute             SkimClick disable button    id                          skimclick123                element_type=Text    operator=not equal
    VerifyAttribute             SkimClick disable button    id                          skimclick123                element_type=Text    operator=!=
    VerifyAttribute             //img                       data-icon                   screen123                   operator=not equal  

VerifyAttributeGreater
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    # greater, should pass
    VerifyAttribute             Button3    data-id                          7                   element_type=Text    operator=greater than
    VerifyAttribute             Button3    data-id                          5                   element_type=Text    operator=>
    # lower, should fail
    Run Keyword And Expect Error    QWebValueError:*                       VerifyAttribute             Button3    data-id                          12346                   element_type=Text    operator=greater than   timeout=2
    # not a number
    Run Keyword And Expect Error    QWebValueError:*not numeric!           VerifyAttribute             //img                       data-icon                   screen1                     operator=greater than      timeout=2

VerifyAttributeGreaterOrEqual
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    # greater or equal, should pass
    VerifyAttribute             Button3    data-id                          7                   element_type=Text    operator=greater than or equal
    VerifyAttribute             Button3    data-id                          12345               element_type=Text    operator=>=
    # less than, should fail
    Run Keyword And Expect Error    QWebValueError:*        VerifyAttribute             input[value\="Button3"]     data-id                     12346    element_type=css        operator=>=    timeout=2

VerifyAttributeLessThan
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    # lower, should pass
    VerifyAttribute             input[value\="Button3"]     data-id                     12347                   element_type=css        operator=less than
    VerifyAttribute             input[value\="Button3"]     data-id                     12347                   element_type=css        operator=<
    # greater, should fail
    Run Keyword And Expect Error    QWebValueError:*        VerifyAttribute             Button3    data-id      39                      element_type=Text        operator=less than    timeout=2
    # not a number
    Run Keyword And Expect Error    QWebValueError:*not numeric!           VerifyAttribute             //img                       data-icon               screen123               operator=less than   timeout=2

VerifyAttributeLessThanOrEqual
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    # lower or equal, should pass
    VerifyAttribute             input[value\="Button3"]     data-id                     12347                   element_type=css        operator=less than or equal
    VerifyAttribute             input[value\="Button3"]     data-id                     12345                   element_type=css        operator=<=
    # greater, should fail
    Run Keyword And Expect Error    QWebValueError:*        VerifyAttribute             input[value\="Button3"]     data-id                     7    element_type=css        timeout=2    operator=<=

VerifyAttributeContains
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    # contains, should pass
    VerifyAttribute             SkimClick disable button    id                          skim      element_type=Text   operator=contains
    VerifyAttribute             input[value\="Button3"]     data-id                     123                     element_type=css        operator=contains
    # not contains, should fail
    Run Keyword And Expect Error    QWebValueError:*        VerifyAttribute             input[value\="Button3"]     data-id                     7    element_type=css       timeout=2     operator=contains

VerifyAttributeNotContains
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    # contains, should pass
    VerifyAttribute             SkimClick disable button    id                          skjm      element_type=Text   operator=not contains
    VerifyAttribute             input[value\="Button3"]     data-id                     3245                     element_type=css        operator=not contains
    # not contains, should fail
    Run Keyword And Expect Error    QWebValueError:*        VerifyAttribute             input[value\="Button3"]     data-id                     5    element_type=css       timeout=2     operator=not contains

VerifyAttributeIncorrectOperator
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    # default operator
    VerifyAttribute             SkimClick disable button    id                          skimclick                   element_type=Text 
    # incorrect operator
    Run Keyword And Expect Error    QWebValueError:*        VerifyAttribute             //img                       data-icon                   screen123                    timeout=2    operator=adsfj
    # correct operator, uppercase
    VerifyAttribute             //img                       data-icon                   screen123                   operator=NOT EQUAL  

VerifyAttributeCheckbox
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/checkbox.html
    ClickText                   Blue
    VerifyAttribute             //*[@id\="ch_1_1"]          checked                     true
    ClickText                   Blue
    Run Keyword And Expect Error                            QWebValueError:*            VerifyAttribute             //*[@id\="ch_1_1"]                        checked              checked

VerifyAttributeNOK
    [Tags]                      VerifyAttribute
    Go To                       http://127.0.0.1:8000/text.html
    Run Keyword And Expect Error      QWebElementNotFoundError:*    VerifyAttribute      //button[@name\="somethingthatdoesnotexist"]    id    something    timeout=2
    Run Keyword And Expect Error      QWebValueError:*              VerifyAttribute      //button             value                Button2              element_type=Text    timeout=2
    # not valid css
    # jailed, Chrome 123
    # Run Keyword And Expect Error      QWebElementNotFoundError:*    VerifyAttribute      //button             value                Button2              element_type=css     timeout=2
    # multiple found css
    Run Keyword And Expect Error      QWebValueError:*              VerifyAttribute      button               value                Button2              element_type=css     timeout=2

VerifyElementTextBorders
    [Tags]                      VerifyElementText    DrawBorders
    Go To                       http://127.0.0.1:8000/text.html
    
    ${no_border_file}           SetVariable            ${CURDIR}/no_border.png
    ${with_border_file}         SetVariable            ${CURDIR}/with_border.png
    Remove Files                ${no_border_file}      ${with_border_file}

    Log Screenshot              ${no_border_file}
    Log Screenshot              # For debugging purposes

    Set Config                  SearchMode             Draw
    Verify Element Text         sentence               more than one
    Sleep                       2                      # make sure there is enough time for border to be drawn
    Log Screenshot              # For debugging purposes
    Log Screenshot              ${with_border_file}
    ${no_border_image}          Get Binary File        ${no_border_file}
    ${with_border_image}        Get Binary File        ${with_border_file}

    Should Not Be Equal         ${no_border_image}     ${with_border_image}
