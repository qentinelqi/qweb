*** Settings ***
Library        QWeb
Documentation  Regression test for self repairing input, this Fails if input field loses focus right after clear
Suite Setup    OpenBrowser  file://${CURDIR}/../resources/self_repairing_example.html  ${BROWSER}  --headless
Suite Teardown  CloseBrowser
Test Timeout        60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
TypeText To Selfrepairing Input Works
    Typetext            Enter your name:        FOOOO
    VerifyNoText        DEFAULTFOOOO
    VerifyInputValue    xpath\=//input[@id\="fname"]   FOOOO

TypeText checkinput value one time check True
    SetConfig      LineBreak       \ue000
    ${message}=    Set Variable    QWebValueError: Expected value*
    Run Keyword And Expect Error    ${message}
    ...   TypeText  //*[@id\="lname"]  Seppo   check=True   timeout=2
    ${config}           GetConfig               CheckInputValue
    ShouldNotBeTrue     ${config}

TypeText checkinput value one time check False
    SetConfig           CheckInputValue         True
    TypeText            //*[@id\="lname"]       Seppo    check=False
    VerifyInputValue    //*[@id\="lname"]       Matti och Teppo och Seppo
    ${config}           GetConfig               CheckInputValue
    ShouldBeTrue        ${config}

TypeText checkinput value verify repaired word with expected param
    SetConfig           CheckInputValue         True
    TypeText            //*[@id\="lname"]       Seppo    expected=Matti och Teppo och Seppo
