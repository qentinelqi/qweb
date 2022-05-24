*** Settings ***
Documentation     Tests for cookies keywords
Library           Collections
Library           Process
Library           OperatingSystem
Library           QWeb
Suite Setup       OpenBrowser    about:blank    ${BROWSER}
Suite Teardown    CloseBrowser
Test Setup        Start Flask Server
Test Teardown     Terminate All Processes
Test Timeout      60 seconds
Force Tags        FLASK


*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Verify That Cookie Is Found
    [Tags]                  PROBLEM_IN_SAFARI
    GoTo                    http://127.0.0.1:5000/
    ${found}                Run Keyword And Return Status   VerifyText      This is a cookie test page.   5
    # Refresh if page is not loaded
    Run Keyword Unless      '${found}' == 'PASS'    run keywords
    ...                     GoTo                    http://127.0.0.1:5000/
    ...                     AND                     VerifyText              This is a cookie test page.   7
    List Cookies
    ${cookie}=              IsCookie                value                   John Doe
    Should Be Equal As Strings   ${cookie}          True

Verify That Cookies Are Deleted
    [Tags]                  PROBLEM_IN_SAFARI
    GoTo                    http://127.0.0.1:5000/
    ${found}                Run Keyword And Return Status   VerifyText      This is a cookie test page.   5
    # Refresh if page is not loaded
    Run Keyword Unless      '${found}' == 'PASS'    run keywords
    ...                     GoTo                    http://127.0.0.1:5000/
    ...                     AND                     VerifyText              This is a cookie test page.   5
    List Cookies
    Delete All Cookies
    ${cookies}=             List Cookies
    Dictionary Should Not Contain Key   ${cookies}  domain
    Dictionary Should Not Contain Key   ${cookies}  httpOnly
    Dictionary Should Not Contain Key   ${cookies}  username
    Dictionary Should Not Contain Key   ${cookies}  path
    Dictionary Should Not Contain Key   ${cookies}  secure
    Dictionary Should Not Contain Key   ${cookies}  value

*** Keywords ***
Start Flask Server
    Set Environment Variable    FLASK_APP    cookies_app.py
    ${path_to_app}=   Evaluate    os.path.realpath(r"${CURDIR}${/}..${/}resources${/}cookies")    modules=os
    ${flask_handle}=    Start Process   flask run    shell=True   cwd=${path_to_app}
    Sleep           5    # Required for the server to start
    Process Should Be Running    ${flask_handle}    Flask server was not running

