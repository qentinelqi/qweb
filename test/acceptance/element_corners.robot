*** Settings ***
Documentation     Tests for corner
Library           QWeb
Suite Setup       OpenBrowser    file://${CURDIR}/../resources/corners.html  ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Input to overlapping elements
    TypeText        First               Tom
    TypeText        Last                Tester
    TypeText        Username/email:     tom.tester123@mailinator.com
    TypeText        Password:           asdasdasd
    TypeText        NIN:                123456-7890
    ClickCheckBox   Email verified:     on                      User
