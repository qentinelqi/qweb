*** Settings ***
Documentation     Tests for handling of alerts
Library           QWeb
Suite Setup       OpenBrowser  ${BASE_URI}/verifylinks.html  ${BROWSER}
...               --headless
Suite Teardown    CloseBrowser
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
VerifyLinks
    [Tags]          VerifyLinks    jailed
    VerifyLinks

VerifyLinksError
    [Tags]          VerifyLinks      Error    jailed
    Run Keyword And Expect Error    QWebException: Found 2 broken link(s):*
    ...             VerifyLinks     ${BASE_URI}/verifybrokenlinks.html    timeout=5