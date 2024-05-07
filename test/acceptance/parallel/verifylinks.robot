*** Settings ***
Documentation     Tests for handling of alerts
Library           QWeb
Suite Setup       OpenBrowser  http://127.0.0.1:8000/verifylinks.html  ${BROWSER}
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
    ...             VerifyLinks     http://127.0.0.1:8000/verifybrokenlinks.html    timeout=5