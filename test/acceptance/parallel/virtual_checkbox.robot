*** Settings ***
Documentation     ClickCheckbox on a checkbox whose input is "visually hidden": a 1x1 px box
...               under a styled one, with no label. The click on the input is intercepted
...               by the styled box. The element that wraps both is what a user clicks, and
...               the page keeps its own state: a `.checked` write on the input changes
...               nothing the page knows about.
Library           QWeb
Suite Setup       Open Page With Visually Hidden Checkboxes
Suite Teardown    CloseBrowser
Test Setup        GoTo    ${BASE_URI}/virtual_checkbox.html
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Selecting a row reaches the page's own state
    ClickCheckbox           Select item First Lead    on
    ClickText               Next
    VerifyText              selected: First Lead

Only the asked row is selected
    ClickCheckbox           Select item Other Lead    on
    ClickText               Next
    VerifyText              selected: Other Lead
    VerifyNoText            First Lead,

Switching a row off again clears it
    ClickCheckbox           Select item First Lead    on
    ClickCheckbox           Select item First Lead    off
    ClickText               Next
    VerifyText              Select at least one record and try again.

On is idempotent
    ClickCheckbox           Select item First Lead    on
    ClickCheckbox           Select item First Lead    on
    ClickText               Next
    VerifyText              selected: First Lead

Aura data table markup
    ClickCheckbox           Select item Aura Lead     on
    ClickText               Next
    VerifyText              selected: Aura Lead

Current SLDS class in the same shape
    ClickCheckbox           Select item LWC Lead      on
    ClickCheckbox           Select item LWC Lead      off
    ClickCheckbox           Select item LWC Lead      on
    ClickText               Next
    VerifyText              selected: LWC Lead

*** Keywords ***
Open Page With Visually Hidden Checkboxes
    OpenBrowser             about:blank               ${BROWSER}    --headless
    # The checkboxes are found by their aria-label, which needs CssSelectors.
    SetConfig               CssSelectors              on
