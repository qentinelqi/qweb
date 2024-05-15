*** Settings ***
Documentation       Test for ClickItem keyword
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}    --headless
Test Setup          GoTo    ${BASE_URI}/items.html
Suite Teardown      CloseBrowser
Test Timeout        60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Click item by it's attribute text
    ClickItem       Infinity
    VerifyText      Infinity is my alt value!
    ClickItem       Lock
    VerifyText      Lock is my title value!
    ClickItem       screen
    VerifyText      screen is my data-icon value!
    ClickItem       paperclip
    VerifyText      paperclip is my aria-label value!
    ClickItem       person
    VerifyText      person is my tooltip value!
    ClickItem       Power
    VerifyText      Power is my data-tooltip value!
    ${message}=     Set Variable    QWebElementNotFoundError: Unable*
    Run Keyword and Expect Error   ${message}    ClickItem    NoAttr      timeout=0.1s

Verify Item Exists
    VerifyItem      Infinity
    VerifyItem      screen
    VerifyItem      Power

Click Item using javascript
    ClickItem       Infinity            js=True
    VerifyText      Infinity is my alt value!
    ClickItem       paperclip           js=True
    VerifyText      paperclip is my aria-label value!

Click Item with CSS Selectors on
    SetConfig       CssSelectors        on
    ClickItem       Infinity
    VerifyText      Infinity is my alt value!
    ClickItem       Lock
    VerifyText      Lock is my title value!
    ClickItem       screen
    VerifyText      screen is my data-icon value!
    ClickItem       paperclip
    VerifyText      paperclip is my aria-label value!
    ClickItem       person
    VerifyText      person is my tooltip value!
    ClickItem       Power
    VerifyText      Power is my data-tooltip value!
    ${message}=     Set Variable    QWebElementNotFoundError: Unable*
    Run Keyword and Expect Error   ${message}    ClickItem    NoAttr      timeout=0.1s

VerifyNoItem
    [tags]           not_exists
    VerifyItem       Infinity
    ${message}=     Set Variable    QWebValueError: Element with attribute value*
    Run Keyword and Expect Error   ${message}   VerifyNoItem  Infinity   timeout=0.5s
    VerifyNoItem    Fisherman

IsItem and IsNoItem
    [tags]           IsItem                     IsNoItem
    ${exists}=       IsItem      person         partial_match=False
    Should Be True   ${exists}
    ${exists}=       IsItem      pers           partial_match=True
    Should Be True   ${exists}
    ClickText        Hide
    ${not_exists}=   IsNoItem    person         partial_match=False      timeout=2
    Should Be True   ${not_exists}
    



    ${message}=     Set Variable    QWebValueError: Element with attribute value*
    Run Keyword and Expect Error   ${message}   VerifyNoItem  Infinity   timeout=0.5s
    VerifyNoItem    Fisherman