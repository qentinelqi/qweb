*** Settings ***
Documentation     Test for selecting active xpath
Library           QWeb
Suite Setup       OpenBrowser    http://127.0.0.1:8000/no_body.html  ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      20 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Verify Text Under One Tag
    [Tags]
    VerifyText              Click the button to open a new browser window.
    ClickText               Avaa ikkuna
    Switch Window           NEW
    Run Keyword and Expect Error       QWebElementNotFoundError*  UseFrame    //frame[@name\='main']
    SetConfig               ActiveAreaXpath       //html
    UseFrame                //frame[@name\='main']
    VerifyText              Lorem ipsum
