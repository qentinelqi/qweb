*** Settings ***
Documentation     Tests for handling of alerts
Library           QWeb
Suite Setup       OpenBrowser    file://${CURDIR}/../resources/alert.html    ${BROWSER}   --headless
Suite Teardown    CloseBrowser
Test Timeout      30 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Accept popup alert
    ClickText           Show alert
    Close alert         accept            2s

Dismiss popup alert
    ClickText           Show alert
    Close alert         dismiss

Leave popup alert
    ClickText           Show alert
    Close alert         Nothing
    Close alert         accept

Alert Not Found
    Run Keyword and Expect Error    QWebDriverError:*    Close alert   accept    2s

IsAlert Not Visible
    ${alert}=           IsAlert
    Should Be Equal     ${alert}    ${FALSE}
    ${alert}=           IsAlert     3s
    Should Be Equal     ${alert}    ${FALSE}

IsAlert Visible
    ClickText           Show alert
    ${alert}=           IsAlert    1s
    Should Be Equal     ${alert}    ${TRUE}
    ${alert}=           IsAlert    1s
    Should Be Equal     ${alert}    ${TRUE}
    Close alert         accept

TypeAlert
    ClickText           Show alert with input field
    TypeAlert           Qentinel Robot
    VerifyText          Qentinel Robot is written on this page.

TypeAlert Leave open
    ClickText           Show alert with input field
    TypeAlert           Robot       Nothing
    ${alert}=           IsAlert    1s
    Should Be Equal     ${alert}    ${TRUE}
    CloseAlert          Accept
    VerifyText          Robot is written on this page.

TypeAlert and dismiss
    ClickText           Show alert with input field
    TypeAlert           Robot       Dismiss
    VerifyNoText        Robot is written on this page.  timeout=2

VerifyAlertText from alert
    ClickText           Show alert with input field
    VerifyAlertText     Tell me your name
    Close alert         accept            2s

GetAlertText from alert
    ClickText           Show alert with input field
    ${TEXT}             GetAlertText
    ShouldBeEqual       ${TEXT}      Tell me your name
    Close alert         accept
