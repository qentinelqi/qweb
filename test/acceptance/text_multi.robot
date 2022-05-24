*** Settings ***
Documentation    Test for text in multiple elements
Library          QWeb
Suite Setup      OpenBrowser  file://${CURDIR}/../resources/multielement_text.html  ${BROWSER}
...              --headless
Suite Teardown   CloseBrowser
Test Timeout     60 seconds

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

Numeric anchors as text
    GoTo            file://${CURDIR}/../resources/num_anchor.html
    Run Keyword and Expect Error
    ...     QWebInstanceDoesNotExistError: Found 2 elements. Given anchor was 456
    ...     ClickText       LINK        456

    # anchor_type argument
    ClickText       LINK        456     anchor_type=text
    VerifyAlertText          correct link was clicked
    CloseAlert      ACCEPT
