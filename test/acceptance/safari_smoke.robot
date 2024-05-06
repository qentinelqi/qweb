*** Settings ***
Library           QWeb
Test Timeout      30 seconds

*** Test Cases ***
Open Safari
    [Tags]          PROBLEM_IN_WINDOWS    PROBLEM_IN_LINUX    PROBLEM_IN_CHROME    PROBLEM_IN_EDGE    PROBLEM_IN_FIREFOX
    OpenBrowser    about:blank    safari
    GoTo    http://127.0.0.1:8000/text.html    timeout=5
    CloseAllBrowsers