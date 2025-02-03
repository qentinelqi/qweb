*** Settings ***
Documentation     Tests for Mouse keywords and coordinates
Library           QWeb
Suite Setup       OpenBrowser    ${BASE_URI}/mouse.html    ${BROWSER}
Suite Teardown    CloseBrowser
Test Teardown     ClickText           Reset Fields
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome

${childnodes}    ${EMPTY}
${childnodes2}    ${EMPTY}
${text}    ${EMPTY}

*** Test Cases ***
Click And Hold with text
    [tags]              mouse  click_and_hold
    VerifyText          Mouse Click and Hold Test
    MouseDown           Click and Hold Me!  element_type=text
    Sleep               2
    MouseUp             Click and Hold Me!  element_type=text
    ${ms}=              GetText     millisecondsField   tag=span
    Should Be True      ${ms} > 2000

Click And Hold with xpath
    [tags]              mouse  click_and_hold
    VerifyText          Mouse Click and Hold Test
    MouseDown           //button[@id\="clickAndHoldButton"]
    Sleep               1
    MouseUp             //button[@id\="clickAndHoldButton"]
    ${ms}=              GetText     millisecondsField   tag=span
    Should Be True      ${ms} > 1000 

Click And Hold with attribute
    [tags]              mouse   click_and_hold
    VerifyText          Mouse Click and Hold Test
    MouseDown           clickAndHoldButton  element_type=item
    Sleep               3
    MouseUp             clickAndHoldButton  element_type=item
    ${ms}=              GetText     millisecondsField   tag=span
    Should Be True      ${ms} > 3000

Click And Hold, incorrect
    [tags]              mouse   click_and_hold
    VerifyText          Mouse Click and Hold Test
    # element not found xpath
    Run Keyword And Expect Error   QWebElementNotFoundError*       MouseDown   //button[@id\="not exists"]     timeout=1

    # element not found, text
    Run Keyword And Expect Error   QWebElementNotFoundError*       MouseDown   Not here     element_type=text   timeout=1

MouseMove
    [tags]              mouse  move
    VerifyText          Mouse Click and Hold Test
    MouseMove           100     100
    VerifyInputValue    X Coordinate    100
    VerifyInputValue    Y Coordinate    100

    # Mutiple moves, chained
    MouseMove           0       0
    MouseMove           300     300
    VerifyInputValue    X Coordinate    300
    VerifyInputValue    Y Coordinate    300

MouseMove, incorrect
    [tags]              mouse  move
    VerifyText          Mouse Click and Hold Test
    Run Keyword And Expect Error   *expected 2 arguments*       MouseMove    100
    Run Keyword And Expect Error   ValueError*     MouseMove    ${EMPTY}    100
    Run Keyword And Expect Error   ValueError*     MouseMove    a   b

Click coordinates
    [tags]              mouse  coordinates
    VerifyText          Mouse Click and Hold Test
    MouseMove           100     100
    VerifyInputValue    X Coordinate    100
    VerifyInputValue    Y Coordinate    100

    ${reset}=           GetWebElement   Reset Fields    element_type=text
    # retunrs dict
    &{coords}=          Evaluate    $reset.location
    # Let's add some buffer since the previous command returns top left corner
    ${x}=               Evaluate    $coords.x+10
    ${y}=               Evaluate    $coords.y+10
    ClickCoordinates    ${x}     ${y}
    VerifyInputValue    X Coordinate    ${EMPTY}
    VerifyInputValue    Y Coordinate    ${EMPTY}


Click coordinates, incorrect coordinates
    [tags]              mouse  coordinates
    VerifyText          Mouse Click and Hold Test
    Run Keyword And Expect Error   *expected 2 arguments*     ClickCoordinates    100
    Run Keyword And Expect Error   ValueError*     ClickCoordinates    ${EMPTY}    100
    Run Keyword And Expect Error   ValueError*     ClickCoordinates    a   b


Right Click button
    [tags]              mouse  right-click_and_hold
    VerifyText          Mouse Click and Hold Test
    VerifyNoText        Option
    RightClick          contextMenuButton   tag=button
    VerifyText          Option 3