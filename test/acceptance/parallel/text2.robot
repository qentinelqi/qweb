*** Settings ***
Documentation                   Tests for text keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 file://${CURDIR}/../../resources/text.html                 ${BROWSER}                  --HEADLESS
Suite Teardown                  CloseBrowser
Test Timeout                    60 seconds

*** Variables ***
${BROWSER}                      chrome
${y_start}                      ${EMPTY}
${y_end}                        ${EMPTY}

*** Test Cases ***
ScanClick
    ScanClick                   Click me                    Clicks: 2                   timeout=15s

ScanClick element is item
    RefreshPage
    ScanClick                   screen                      Clicks: 2                   el_type=item

ScanClick xpath
    RefreshPage
    ScanClick                   //*[text()\="Click me"]     Clicks: 2                   interval=1                  timeout=10s
    ScanClick                   Click me                    xpath\=//*[text()\="4"]

ScanClick wrong pre condition
    ${message}=                 Set Variable                QWebValueError: Text to appear is already visible.
    Run Keyword and Expect Error                            ${message}                  ScanClick                   Click me                    Click me        timeout=2

SkimClick
    RefreshPage
    SkimClick                   Button5
    SkimClick                   Click me                    Clicks: 0

SkimClick element is item
    RefreshPage
    SkimClick                   screen                      Clicks: 0                   el_type=item

SkimClick wrong pre condition
    ${message}=                 Set Variable                QWebValueError: Text to disappear is not visible before click.
    Run Keyword and Expect Error                            ${message}                  SkimClick                   Click me                    Qentiro         timeout=2

SkimClick xpath
    RefreshPage
    SkimClick                   //*[text()\="Click me"]     Clicks: 0                   timeout=15s
    SkimClick                   Click me                    xpath\=//*[text()\="1"]

SkimClick slowly disabling button
    RefreshPage
    SkimClick                   SkimClick disable button    interval=1
    VerifyText                  skim/scan clicked!

SkimClickCorrectErr
    [tags]
    ${message}=                 Set Variable                QWebValueError: Page contained the text "Click me" after timeout*
    Run Keyword and Expect Error                            ${message}                  SkimClick                   HoverDropdown               Click me        timeout=2

ScanClickCorrectErr2
    [tags]                      err
    RefreshPage
    ${message}=                 Set Variable                QWebElementNotFoundError: Unable to find element for locator skim/scan clicked!*
    Run Keyword and Expect Error                            ${message}                  ScanClick                   HoverDropdown               skim/scan clicked!    timeout=2

ScanClick with disabling button
    RefreshPage
    ScanClick                   SkimClick disable button    skim/scan clicked!          interval=1

Click While
    [tags]                      whileuntil
    RefreshPage
    ClickWhile                  Button5
    ClickWhile                  Clicks: 0                   Click me

Click While wrong pre condition
    [tags]                      whileuntil
    ${message}=                 Set Variable                QWebValueError: Text to disappear is not visible before click.
    Run Keyword and Expect Error                            ${message}                  ClickWhile                  Qentiro                     Click me        timeout=2

Click while xpath
    [tags]                      whileuntil
    RefreshPage
    ClickWhile                  Clicks: 0                   //*[text()\="Click me"]     timeout=15s
    ClickWhile                  xpath\=//*[text()\="1"]     Click me

Click Until
    [tags]                      whileuntil
    RefreshPage
    ClickUntil                  Clicks: 2                   Click me                    interval 1s                 timeout=15s

Click Until xpath
    [tags]                      whileuntil
    RefreshPage
    ClickUntil                  Clicks: 3                   //*[text()\="Click me"]     interval=2                  timeout=8s
    ClickUntil                  xpath\=//*[text()\="7"]     Click me                    interval=1

Click Until wrong pre condition
    [tags]                      whileuntil
    ${message}=                 Set Variable                QWebValueError: Text to appear is already*
    Run Keyword and Expect Error                            ${message}                  Click Until                 Click me                    Click me        timeout=2

ClickUntil wait element to appear
    [tags]                      whileuntil
    RefreshPage
    ClickUntil                  hidden-treasure             Show hidden                 element=True
    ${message}=                 Set Variable                QWebValueError: Element to appear is already*
    Run Keyword and Expect Error                            ${message}                  Click Until                 hidden-treasure             Show hidden     element=True

ClickWhile wait element to disappear
    [tags]                      whileuntil
    ClickWhile                  hidden-treasure             Hide Text                   element=True
    ${message}=                 Set Variable                QWebValueError: Element to disappear is not visible*
    Run Keyword and Expect Error                            ${message}                  ClickWhile                  hidden-treasure             Hide Text       element=True

ClickItemWhile
    RefreshPage
    ClickItemWhile              Clicks: 0                   screen
    ${message}=                 Set Variable                QWebValueError: Text to disappear is not visible*
    Run Keyword and Expect Error                            ${message}                  ClickItemWhile              Clicks: 0                   screen

ClickItemUntil
    ClickItemUntil              Clicks: 4                   screen                      interval=2
    ${message}=                 Set Variable                QWebValueError: Text to appear*
    Run Keyword and Expect Error                            ${message}                  ClickItemUntil              Clicks: 4                   screen          timeout=2

Hover Text small window
    [Tags]                      PROBLEM_IN_FIREFOX
    # Bug https://qentinel.visualstudio.com/Pace_libraries/_workitems/edit/3364
    SetConfig                   WindowSize                  576X356
    HoverText                   Button1
    VerifyNoText                Hover Link
    HoverText                   Hover Dropdown
    VerifyText                  Hover Link

ScrollText
    Execute Javascript          return window.pageYOffset                               $y_start
    ScrollText                  TextToScroll                timeout=3
    Execute Javascript          return window.pageYOffset                               $y_end
    Run Keyword If              ${y_end} <= ${y_start}      Fail                        Did not scroll

VerifyText quotes
    [Tags]                      Quotes
    VerifyText                  40"                                                     partial_match=True
    VerifyText                  Text with quote character: 40"                          partial_match=False
    VerifyText                  O'Reilly                                                partial_match=True
    VerifyText                  Text with single quote character: O'Reilly              partial_match=False
    VerifyText                  Button's text has 'single' & "double"                   partial_match=True
    VerifyText                  Button's text has 'single' & "double"                   partial_match=False

ClickText quotes
    [Tags]                      Quotes
    VerifyElement               //*[text()\=concat('Text with quote character: 40', '"')]
    VerifyElement               //*[text()\=concat('50', '"')]
    ClickElement                //*[text()\='50"']
    VerifyText                  fifty inch was clicked
    ClickText                   Button's text has 'single' & "double"
    VerifyText                  single & double quotes clicked

Child and Parents - Click Identifier
    VerifyNoText                textblock clicked!          timeout=2
    ClickText                   Identifying text
    VerifyText                  textblock clicked!

Child and Parents - Click parent
    [tags]                      PROBLEM_IN_FIREFOX
    VerifyNoText                parent clicked!             timeout=2
    ClickText                   Identifying text            parent=div
    VerifyText                  parent clicked!

Child and Parents - Click child
    VerifyNoText                smiley clicked!             timeout=2
    ClickText                   Identifying text            child=span
    VerifyText                  smiley clicked!

Child and Parents - JS click Identifier
    VerifyNoText                textblock clicked!          timeout=2
    ClickText                   Identifying text            js=True
    VerifyText                  textblock clicked!

Child and Parents - JS click parent
    VerifyNoText                parent clicked!             timeout=2
    ClickText                   Identifying text            parent=div                  js=True
    VerifyText                  parent clicked!

Child and Parents - JS click child
    VerifyNoText                smiley clicked!             timeout=2
    ClickText                   Identifying text            child=span                  JS=True
    VerifyText                  smiley clicked!

Doubleclick
    [tags]                      PROBLEM_IN_FIREFOX          Doubleclick
    VerifyNoText                doubleclick test clicked!
    SetConfig                   DoubleClick                 On
    ClickText                   double-click test.
    VerifyText                  doubleclick test clicked!
    SetConfig                   DoubleClick                 Off

Doubleclick with arguments
    [tags]                      Doubleclick
    RefreshPage
    VerifyNoText                doubleclick test clicked!
    ClickText                   double-click test.          doubleclick=True
    VerifyText                  doubleclick test clicked!

Doubleclick element with arguments
    [tags]                      Doubleclick
    RefreshPage
    VerifyNoText                doubleclick test clicked!
    ClickElement                //*[@id\="doubleclick test"]                            doubleclick=True
    VerifyText                  doubleclick test clicked!

Doubleclick item with arguments
    [tags]                      Doubleclick
    RefreshPage
    VerifyNoText                doubleclick test clicked!
    ClickItem                   doubleclick test            doubleclick=True
    VerifyText                  doubleclick test clicked!

WriteText error in headless mode
    [tags]                      PROBLEM_IN_FIREFOX          PROBLEM_IN_SAFARI
    [Documentation]             Headless mode is used in suite setup, if that gets changed this test needs
    ...                         to be fixed as well.
    ${error}                    Set Variable                QWebEnvironmentError: Running in headless*
    Run Keyword and Expect Error                            ${error}                    WriteText                   Foobar