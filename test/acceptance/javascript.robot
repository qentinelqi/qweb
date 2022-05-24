*** Settings ***
Documentation     Tests for Javascript keyword
Library           QWeb
Suite Setup       OpenBrowser  file://${CURDIR}/../resources/javascript.html  ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      30 seconds

*** Variables ***
${BROWSER}    chrome
${TITLE}      ${EMPTY}

*** Test Cases ***
Execute Javascript
    VerifyNoText            Text written by javascript
    ExecuteJavascript       document.getElementsByTagName("p")[0].innerText\="Text written by javascript";
    VerifyText              Text written by javascript

Get page title to variable via javascript
    ExecuteJavascript       return document.title;  $TITLE
    Should Be Equal         ${TITLE}                Javascript Acceptance Tests

Invalid variable format
    Run Keyword And Expect Error   QWebValueError: Invalid variable syntax 'TITLE3'.      ExecuteJavascript
    ...   return document.title;   TITLE3

    
