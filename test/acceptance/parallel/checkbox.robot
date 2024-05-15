*** Settings ***
Documentation     Tests for handling of checkboxes
Library           QWeb
Library           Dialogs
Suite Setup       OpenBrowser  ${BASE_URI}/checkbox.html  ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Check checkbox status is enabled
    VerifyCheckboxStatus    I have a bike           enabled

Check checkbox status is disabled
    VerifyCheckboxStatus    I should be disabled    disabled

ClickCheckbox on
    ClickCheckbox           I have a bike           on

Click double ClickCheckbox
    ClickCheckbox           I have a bike           off
    ClickCheckbox           I have a bike           on
    ClickCheckbox           I have a bike           off

ClickCheckbox on with verify
    ClickCheckbox           I have a bike           on
    VerifyCheckboxValue     I have a bike           on

Click double checkobx with verify
    ClickCheckbox           I have a car            on
    VerifyCheckboxValue     I have a car            on
    ClickCheckbox           I have a car            off
    VerifyCheckboxValue     I have a car            off

Find with xpath on
    ClickCheckbox           xpath\=//*[@id\="ch2"]    on
    VerifyCheckboxValue     I have a car            on

Find with xpath off
    ClickCheckbox           xpath\=//*[@id\="ch2"]    off
    VerifyCheckboxValue     I have a car            off

Click table checkbox
    ClickCheckbox           Sample text             on
    VerifyCheckboxValue     Sample text             on

Click same name without anchor, default to 1
    SetConfig               CssSelectors            off
    ClickCheckbox           Blue                    on
    VerifyCheckboxValue     Blue                    on              1
    VerifyCheckboxValue     Blue                    off             2

Use index anchor
    ClickCheckbox           Blue                    on              2
    VerifyCheckboxValue     Blue                    on              2

Checkbox using css 1
    SetConfig               CssSelectors            on
    VerifyCheckboxStatus    I have a bike           enabled
    VerifyCheckboxStatus    I should be disabled    disabled
    ClickCheckbox           I have a bike           on
    ClickCheckbox           I have a bike           off
    ClickCheckbox           I have a bike           on
    ClickCheckbox           I have a bike           off
    ClickCheckbox           I have a bike           on
    VerifyCheckboxValue     I have a bike           on
    ClickCheckbox           I have a car            on
    VerifyCheckboxValue     I have a car            on
    ClickCheckbox           I have a car            off
    VerifyCheckboxValue     I have a car            off
    SetConfig               CssSelectors            off

Checkbox using css 2
    SetConfig               CssSelectors            on
    ClickCheckbox           Red                     on
    ClickCheckbox           Sample text             on
    VerifyCheckboxValue     Sample text             on
    ClickCheckbox           Blue                    on
    ClickCheckbox           Blue                    on              2
    VerifyCheckboxValue     Blue                    on
    ClickCheckbox           Blue                    off
    VerifyCheckboxValue     Red                     on
    VerifyCheckboxValue     Blue                    off
    SetConfig               CssSelectors            off

Delayed Checkbox
    ClickText               Show checkbox
    ClickCheckbox           Hiddenbox               on
    VerifyCheckboxValue     Hiddenbox               on

SalesForce Checkbox
    VerifyText             mnptye
    ClickCheckbox          mnptye         On
    VerifyCheckboxValue    mnptye         On
    VerifyCheckboxValue    mnptye         On             1s

No Text Found
    ${msg}=     Run Keyword And Expect Error    *    ClickCheckbox    NotFound    On    1    2
    Should Contain  ${msg}  QWebElementNotFoundError: Unable to find element for locator

No Checkbox found
    GoTo                    ${BASE_URI}/text.html
    Run Keyword And Expect Error       QWebElementNotFoundError: Unable*   ClickCheckbox   Lorem   On       1       2
