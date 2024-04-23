*** Settings ***
Library           QWeb
Test Timeout      10 seconds
Suite Teardown    CloseAllBrowsers

*** Test Cases ***
Open Safari
    [Tags]          PROBLEM_IN_WINDOWS    PROBLEM_IN_LINUX    PROBLEM_IN_CHROME    PROBLEM_IN_EDGE    PROBLEM_IN_FIREFOX
    OpenBrowser    about:blank    safari