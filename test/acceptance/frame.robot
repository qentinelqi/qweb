*** Settings ***
Documentation     Tests for frame keywords
Library           QWeb
Suite Setup       OpenBrowser    file://${CURDIR}/../resources/frame.html    ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Refresh Page
    [Tags]                  PROBLEM_IN_SAFARI
    ClickText               Button1
    VerifyText              Button1 was clicked
    RefreshPage
    VerifyNoText            Button1 was clicked

Use Frame And Use Page
    [Tags]                  PROBLEM_IN_SAFARI
    VerifyText              Text not in frame
    VerifyText              Text in frame
    VerifyText              Text not in frame
    VerifyText              Text in frame

Automatic frame search text elements
    [Tags]                  PROBLEM_IN_SAFARI
    SetConfig               DefaultDocument         True
    VerifyNoText            Button3 was clicked
    ScrollText              Button3
    ClickText               Button3
    VerifyText              Button3 was clicked
    ScrollText              Input fields with

Automatic frame search input elements
    [tags]                  inputs                  PROBLEM_IN_SAFARI
    TypeText                First input             Robot
    TypeText                Second input            QENROB
    TypeText                Cell 1 input            20022019
    TypeText                Cell 2                  Test
    TypeText                Cell 3                  Last one in this row
    TypeText                Misplaced input         I'am at wrong place!!
    ${value}                GetInputValue           Misplaced input
    ShouldBeEqual           ${value}                I'am at wrong place!!
    TypeText                Some text               I'am catching you too..
    Sleep                   2                       # takes time in Mac on CI machines
    ${value}                GetInputValue           Some text
    ShouldbeEqual           ${value}                I'am catching you too..

Automatic frame search table elements
    [Tags]                  PROBLEM_IN_SAFARI
    UseTable                Sample
    TypeText                r4c1                    Qentiro
    TypeText                r4c2                    Robot
    TypeText                r4c3                    17
    TypeText                r4c4                    2019-02-24
    VerifyInputValue        r4c1                    Qentiro
    VerifyInputValue        r4c2                    Robot
    VerifyInputValue        r4c3                    17
    VerifyInputValue        r4c4                    2019-02-24
    Run Keyword And Expect Error       QWebValueError: Expected value*
    ...   VerifyInputValue       r4c4   2019-02-23       timeout=2


Automatic frame search checkbox elements
    [Tags]                  PROBLEM_IN_SAFARI
    SetConfig               CSSSelectors            off
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

Automatic frame search dropdown elements
    [Tags]                  PROBLEM_IN_SAFARI
    SetConfig               CSSSelectors            on
    Dropdown                label without           Rules
    VerifySelectedOption    label without           Rules
    VerifyOption            label without           OK
    VerifyOption            label without           Qentinel

Automatic frame search back and forth between frames
    [Tags]                  PROBLEM_IN_SAFARI
    Dropdown                label without           Rules
    VerifySelectedOption    label without           Rules
    TypeText                First input             Robot
    TypeText                Second input            QENROB
    VerifyText              Text not in frame
    UseTable                Sample
    TypeText                r4c1                    Qentiro
    ScrollText              Button3
    ClickText               Button3
    VerifyText              Button3 was clicked
    VerifyText              Lorem ipsum dolor sit amet
    ScrollText              Input fields with

IsText in different frame
    [Tags]                  istext                 PROBLEM_IN_SAFARI
    ClickCheckbox           I have a bike          on
    ${found}=               IsText                 Last name:
    Should Be Equal         ${found}               ${TRUE}

IsNoText in different frame
    [Tags]                  istext                 PROBLEM_IN_SAFARI
    ClickCheckbox           I have a bike          on
    ${notfound}=            IsNoText               Last name:    0.1s
    Should Be Equal         ${notfound}            ${FALSE}

Upload files with index
    [Tags]              PROBLEM_IN_SAFARI
    UploadFile          1                       test1.txt
    ExecuteJavaScript   return document.querySelector('#myFile1').value   $value
    ShouldBeEqual       ${value}                C:\fakepath\test1.txt
    UploadFile          2                       test2.txt
    ExecuteJavaScript   return document.querySelector('#myFile2').value   $value
    ShouldBeEqual       ${value}                C:\fakepath\test2.txt

Upload files with locator
    [Tags]              PROBLEM_IN_SAFARI
    UploadFile          Uploadme                       test1.txt
    ExecuteJavaScript   return document.querySelector('#myFile1').value   $value
    ShouldBeEqual       ${value}                       C:\fakepath\test1.txt

Upload with xpath
    UploadFile          //*[@id\='myFile3']    test2.txt
    ExecuteJavaScript   return document.querySelector('#myFile3').value   $value
    ShouldBeEqual       ${value}                       C:\fakepath\test2.txt