*** Settings ***
Documentation       Tests for text in html5 accordion elements
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}    --headless
Test Setup          GoTo    file://${CURDIR}/../resources/accordions_and_modals.html
Suite Teardown      CloseBrowser
Test Timeout        1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Click Element Under fast accordion
    [Documentation]  These are tests for html5 elements that are slow but not usually detected by xhr
    VerifyText      Accordion and modal elements
    ClickText       Accordion Element 1
    ClickText       LinkToText
    VerifyText      HoverDropdown

Click Element Under slow accordion
    VerifyText      Accordion and modal elements
    ClickText       Accordion Element 2
    ClickText       OtherLinkToText
    VerifyText      HoverDropdown

Modal Element
    ClickText       Modal Element 1
    ClickText       Click this text to close me!

Filtering based on modal
    # Default, no filtering based on modal
    ClickText                Modal Element 1
    ${found}=                IsText                        Accordion Element 1
    Should Be True           ${found}                    

    # Filter by modal
    ${prev}=                 SetConfig                     IsModalXPath                  //div[@id="modal_element"]
    Sleep  3   # TESTING
    ${found}=                IsText                        Accordion Element 1
    Should Not Be True       ${found}

    SetConfig                IsModalXPath                  ${prev}       