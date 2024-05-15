*** Settings ***
Library           QWeb
Test Timeout      30 seconds
Suite Setup     Check Http Server

*** Variables ***
${ON_HTTP_SERVER}=    ${FALSE}

*** Test Cases ***
Open Safari
    [Tags]          PROBLEM_IN_WINDOWS    PROBLEM_IN_LINUX    PROBLEM_IN_CHROME    PROBLEM_IN_EDGE    PROBLEM_IN_FIREFOX
    OpenBrowser    about:blank    safari
    GoTo    ${BASE_URI}/text.html    timeout=5
    CloseAllBrowsers

*** Keywords ***
Check Http Server
    IF    $ON_HTTP_SERVER
        ${BASE_URI}=    Set Variable    http://127.0.0.1:8000
    ELSE
        ${BASE_URI}=    Set Variable    file:///${CURDIR}/../resources
    END
    Set Global Variable    ${BASE_URI}