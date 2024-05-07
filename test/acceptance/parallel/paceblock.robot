*** Settings ***
Documentation    Tests for input keywords
Library          QWeb
Library          OperatingSystem
Suite Setup      OpenBrowser    http://127.0.0.1:8000/input.html    ${BROWSER}  --headless
Suite Teardown   CloseBrowser
Test Timeout     60 seconds

*** Variables ***
${BROWSER}    chrome
${Bar}        1
${foobar}     timeout
${TEST_VAR}   None

*** Test Cases ***
Run Block basic robot kw without arguments used as PaceBlock
    [tags]                  PROBLEM_IN_FIREFOX
    RunBlock                FooBarBaz       exp_handler=Setter

Run Block basic robot kw with arguments used as PaceBlock
    [tags]                  PROBLEM_IN_FIREFOX
    Goto                    http://127.0.0.1:8000/text.html
    RunBlock                Clicks      Clicks: 5      timeout=15

RunBlock For loop in robot kw
    [tags]                  PROBLEM_IN_FIREFOX
    Goto                    http://127.0.0.1:8000/input.html
    RefreshPage
    RunBlock                TypeThreeTimes    timeout=5

Appstate without argument
    [tags]              Appstate
    Appstate            Clickbutton
    VerifyText          Clicks: 1

Appstate with argument
    [tags]              Appstate
    Goto                  http://127.0.0.1:8000/text.html
    RefreshPage
    Appstate            Clicks              Clicks: 1
    VerifyText          Clicks: 1

*** Keywords ***

FooBarBaz
    ShouldBeEqual         ${TEST_VAR}        teardown
    TypeText              The Brave          Test    timeout=2  clear_key={NULL}
    TypeText              jeuda              Test
    TypeText              field4             ${BROWSER}  ${foobar}=${1}  anchor=${Bar}
    ${foo}                GetInputValue      jeuda
    TypeText              jeuda              ${foo}
    TypeText              field5             Qentinel
    VerifyInputValue      field4             ${BROWSER}      timeout=1
    VerifyInputValue      field5             Qentinel
    ${TEXT}               GetInputValue      field5      between=???nel
    ShouldBeEqual         ${TEXT}            Qenti
    TypeText              field5             ${TEXT}
    VerifyInputValue      jeuda              Test
    VerifyInputValue      field5             Qenti           timeout=0.1s
    VerifyInputValue      The Brave          TestTestTest    timeout=0.5s

Clickbutton
    Goto                  http://127.0.0.1:8000/text.html
    RefreshPage
    ClickText             Click me      #Every click = + 1 to counter

Clicks
    [Arguments]           ${text}
    ClickText             Click me      #Every click = + 1 to counter
    VerifyText            ${text}             2s

TypeThreeTimes
    FOR    ${i}    IN RANGE    3
        TypeText          The Brave          Test    clear_key={NULL}
    END
    VerifyInputValue      The Brave          TestTestTestTestTestTest  timeout=0.5s

Setter
    SetSuiteVariable      ${TEST_VAR}        teardown