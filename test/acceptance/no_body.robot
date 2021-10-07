*** Settings ***
Documentation     Test for selecting active xpath
Library           QWeb
Suite Setup       OpenBrowser    file://${CURDIR}/../resources/no_body.html  ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Verify Text Under One Tag
    [Tags]                  PROBLEM_IN_SAFARI
    VerifyText              Click the button to open a new browser window.
    ClickText               Avaa ikkuna
    Switch Window           NEW
    Run Keyword and Expect Error       QWebElementNotFoundError*  UseFrame    //frame[@name\='main']
    SetConfig               ActiveAreaXpath       //html
    UseFrame                //frame[@name\='main']
    VerifyText              Lorem ipsum
