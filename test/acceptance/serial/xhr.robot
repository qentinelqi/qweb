*** Settings ***
Documentation    Tests page using XHR
Library          Process
Library          OperatingSystem
Library          QWeb
Suite Setup      Start Flask Server And Open Browser
Suite Teardown   XHR Teardown
Test Timeout     1min
Force Tags       FLASK

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Wait Xhr Within Verify Text Keyword
    [Tags]    PROBLEM_IN_SAFARI
    SetConfig       DefaultTimeout          10
    GoTo            http://127.0.0.1:5000/
    VerifyText      Load xhr    10    # Make sure page is present
    VerifyNoText    Text retrieved using xhr
    ClickText       Load xhr
    VerifyText      Text retrieved using xhr

Modify Xhr and new function
    [Tags]    PROBLEM_IN_SAFARI
    ${new_xhr}=     Evaluate                  lambda:True
    ${previous}=    Set Wait Function         ${new_xhr}
    GoTo            http://127.0.0.1:5000/
    ${found}    Run Keyword And Return Status    ClickText       Load xhr
    Run Keyword Unless    '${found}' == 'PASS'   run keywords
    ...    GoTo     http://127.0.0.1:5000/
    ...    AND      ClickText       Load xhr
    ${old}=         Set Wait Function         ${previous}
    GoTo            http://127.0.0.1:5000/
    ${found}    Run Keyword And Return Status    ClickText       Load xhr
    Run Keyword Unless    '${found}' == 'PASS'   run keywords
    ...    GoTo     http://127.0.0.1:5000/
    ...    AND      ClickText       Load xhr

Modify Xhr with string
    Run Keyword And Expect Error    ValueError: Argument needs to be callable: bar        Set Wait Function    bar

Modify Xhr and unknown type
    Run Keyword And Expect Error    ValueError: Argument needs to be callable:${SPACE}
    ...    Set Wait Function    ${EMPTY}

*** Keywords ***
Start Flask Server And Open Browser
    Set Environment Variable    FLASK_APP    xhr_app.py
    ${flask_handle}=    Start Process   flask run    shell=True   cwd=${CURDIR}${/}..${/}..${/}resources${/}xhr
    Sleep           5    # Required for the server to start
    Process Should Be Running    ${flask_handle}    Flask server was not running
    OpenBrowser    about:blank    ${BROWSER}  --headless

XHR Teardown
    Terminate All Processes
    CloseBrowser