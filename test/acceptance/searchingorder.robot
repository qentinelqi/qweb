*** Settings ***
Documentation     Full matches should always be first if text-attr is not used
Library           QWeb
Suite Setup       OpenBrowser  file://${CURDIR}/../resources/frame.html  ${BROWSER}
Suite Teardown    CloseBrowser
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
InputElements
    [tags]                  inputsorder
    # Hover needed in ff 89
    HoverText               Second input
    TypeText                Cell 1          Qentinel
    VerifyInputValue        field7          Qentinel  timeout=3
    TypeText                Cell 1 input    Robot
    VerifyInputValue        field8          Robot
    TypeText                Cell 1 input:   Test Automation
    VerifyInputValue        field3          Test Automation
    TypeText                Cell 1 input    FooBar      index=2         visibility=False
    VerifyInputValue        field3          FooBar

CheckboxElements
    SetConfig               WindowSize              1920x1080
    RefreshPage
    ClickCheckbox           I have a                on
    VerifyCheckboxValue     I have a bike           on
    ClickCheckbox           Sample text             on
    VerifyCheckboxValue     Sample text             on
    ClickCheckBox           Blue                    on    index=2
    VerifyCheckboxValue     Blue                    on    index=2
    VerifyCheckboxValue     Blue                    off
    ClickCheckbox           Blue:                   on
    VerifyCheckboxValue     ch_1_4                  on
    ClickCheckBox           Bl                      on
    VerifyCheckboxValue     ch_1_5                  on
    #Old way. Pics first with text Bl:
    ClickCheckbox           Bl                      on   qweb_old=True
    VerifyCheckboxValue     ch_1_1                  on
    ScanClick               Show checkbox           Hiddenbox   interval=3
    ClickCheckbox           Hiddenbox               on

DropDownElements
    DropDown                drop                    test3
    VerifySelectedOption    drop                    test3
    VerifySelectedOption    dropdown                test1
    VerifyText              Hiddenbox               visibility=False

DropDownElementsWithCapsKwargs
    DropDown                drop                    test3
    VerifySelectedOption    drop                    test3
    VerifySelectedOption    dropdown                test1
    VerifyText              Hiddenbox               VISIBILITY=False
