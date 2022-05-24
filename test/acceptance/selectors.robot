*** Settings ***
Documentation     Tests for selector attribute
Library           QWeb
Suite Setup       OpenBrowser  file://${CURDIR}/../resources/frame.html  ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      20 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Use selector attribute instead of xpath syntax
    [tags]	PROBLEM_IN_FIREFOX
    TypeText                n               Qentiro        selector=id   timeout=1
    VerifyInputValue        Name            Qentiro
    HoverElement            screen          selector=data-icon
    ClickElement            screen          selector=data-icon
    VerifyText              Clicks: 1
    HoverText               Flow
    DropDown                dropdown9       optionx        selector=id
    VerifySelectedOption    dropdown9       optionx        selector=id

