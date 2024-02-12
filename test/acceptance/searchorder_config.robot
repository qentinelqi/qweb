*** Settings ***
Documentation     Full matches should always be first if text-attr is not used
Library           QWeb
Suite Setup       OpenBrowser  file://${CURDIR}/../resources/text.html  ${BROWSER}
Suite Teardown    CloseBrowser
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
VerifyText SearchDirection
    [Tags]                      SearchDirection
    [Teardown]                  ResetConfig                 SearchDirection
    VerifyText                  Current scroll                                          anchor=TextToScroll
    # text is below, but setting is not enforced
    SetConfig                   SearchDirection                                         up
    VerifyText                  Current scroll                                          anchor=TextToScroll
    # text is below, setting is enforced
    SetConfig                   SearchDirection                                         !up
    Run Keyword And Expect Error                        QWebElementNotFound*            VerifyText                  Current scroll    timeout=3                                       anchor=TextToScroll    timeout=3
    
ClickText SearchDirection
    [Tags]                      SearchDirection
    [Teardown]                  ResetConfig                 SearchDirection
    RefreshPage
    # closest
    ClickText                   Click me    anchor=Show hidden
    VerifyText                  Clicks: 1
    RefreshPage
    
    # searchdirection not enforced
    SetConfig                   SearchDirection                                         left
    ClickText                   Click me    anchor=Show hidden
    VerifyText                  Clicks: 1
    RefreshPage

    # searchdirection not enforced
    SetConfig                   SearchDirection                                         !left
    Run Keyword And Expect Error        QWebElementNotFound*     ClickText              Click me    anchor=Show hidden        timeout=3
    VerifyNoText                Clicks: 1                        timeout=2