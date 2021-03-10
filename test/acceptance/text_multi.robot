*** Settings ***
Documentation    Test for text in multiple elements
Library          QWeb
Suite Setup      OpenBrowser  file://${CURDIR}/../resources/multielement_text.html  ${BROWSER}
...              --headless
Suite Teardown   CloseBrowser
Test Timeout     1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Multiple found elements without anchor
    ClickText       Button
    VerifyText      Button1 was clicked
    RefreshPage

Multiple found elements with anchor
    RefreshPage
    ClickText       Button      3
    VerifyText      Button3 was clicked

Nonexisting index
    RefreshPage
    Run Keyword and Expect Error
    ...     QWebInstanceDoesNotExistError: Found 4 elements. Given anchor was 9
    ...     ClickText       Button      9

Hover multi
    HoverText       Hover Dropdown
    VerifyText      Hover Link1
