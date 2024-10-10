*** Settings ***
Documentation                   Tests for frame keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 ${BASE_URI}/frame.html                ${BROWSER}    --headless
Suite Teardown                  CloseBrowser
Test Timeout                    60 seconds

*** Variables ***
${BROWSER}                      chrome
${value}                        ${EMPTY}

*** Test Cases ***
Refresh Page
    [Tags]                      Frame    Refresh
    ClickText                   Button1
    VerifyText                  Button1 was clicked
    RefreshPage
    VerifyNoText                Button1 was clicked    timeout=5
    SetConfig                   StayInCurrentFrame    False
    VerifyText                  Text in frame

Back & Forward
    [Tags]                      Frame    Back    Forward
    GoTo                        about:blank
    VerifyUrl                   about:blank
    VerifyNoText                Button1
    Back
    ${url}=                     GetUrl
    Should Not Be Equal         ${url}                      about:blank
    VerifyText                  Button1
    Forward
    VerifyNoText                Button1
    ${url}=                     GetUrl
    Should Be Equal             ${url}                      about:blank
    Back
    RefreshPage

Use Frame And Use Page
    [Tags]                      Frame
    VerifyText                  Text not in frame
    VerifyText                  Text in frame
    VerifyText                  Text not in frame
    VerifyText                  Text in frame

Automatic frame search text elements
    [Tags]                      Frame                   
    SetConfig                   DefaultDocument             True
    VerifyNoText                Button3 was clicked
    ScrollText                  Button3
    ClickText                   Button3
    VerifyText                  Button3 was clicked
    ScrollText                  Input fields with

Automatic frame search input elements
    [tags]                      inputs
    TypeText                    First input                 Robot
    TypeText                    Second input                QENROB
    TypeText                    Cell 1 input                20022019
    TypeText                    Cell 2                      Test
    TypeText                    Cell 3                      Last one in this row
    TypeText                    Misplaced input             I'am at wrong place!!
    ${value}                    GetInputValue               Misplaced input
    ShouldBeEqual               ${value}                    I'am at wrong place!!
    TypeText                    Some text                   I'am catching you too..
    Sleep                       2                           # takes time in Mac on CI machines
    ${value}                    GetInputValue               Some text
    ShouldbeEqual               ${value}                    I'am catching you too..

Automatic frame search table elements
    [Tags]                      Frame
    UseTable                    Sample
    TypeText                    r4c1                        Qentiro
    TypeText                    r4c2                        Robot
    TypeText                    r4c3                        17
    TypeText                    r4c4                        2019-02-24
    VerifyInputValue            r4c1                        Qentiro
    VerifyInputValue            r4c2                        Robot
    VerifyInputValue            r4c3                        17
    VerifyInputValue            r4c4                        2019-02-24
    Run Keyword And Expect Error                            QWebValueError: Expected value*
    ...                         VerifyInputValue            r4c4                        2019-02-23    timeout=2


Automatic frame search checkbox elements
    [Tags]                      Frame
    SetConfig                   WindowSize                  1920x1080
    SetConfig                   CSSSelectors                off
    RefreshPage
    VerifyText                  CheckBox
    VerifyCheckboxStatus        I have a bike               enabled
    VerifyCheckboxStatus        I should be disabled        disabled
    ClickCheckbox               I have a bike               on
    ClickCheckbox               I have a bike               off
    ClickCheckbox               I have a bike               on
    ClickCheckbox               I have a bike               off
    ClickCheckbox               I have a bike               on
    VerifyCheckboxValue         I have a bike               on
    ClickCheckbox               I have a car                on
    VerifyCheckboxValue         I have a car                on
    ClickCheckbox               I have a car                off
    VerifyCheckboxValue         I have a car                off

Automatic frame search dropdown elements
    [Tags]                      Frame
    SetConfig                   CSSSelectors                on
    Dropdown                    label without               Rules
    VerifySelectedOption        label without               Rules
    VerifyOption                label without               OK
    VerifyOption                label without               Qentinel

Automatic frame search back and forth between frames
    [Tags]                      Frame                
    Dropdown                    label without               Rules
    VerifySelectedOption        label without               Rules
    TypeText                    First input                 Robot
    TypeText                    Second input                QENROB
    VerifyText                  Text not in frame
    UseTable                    Sample
    TypeText                    r4c1                        Qentiro
    ScrollText                  Button3
    ClickText                   Button3
    VerifyText                  Button3 was clicked
    VerifyText                  Lorem ipsum dolor sit amet
    ScrollText                  Input fields with

IsText in different frame
    [Tags]                      istext
    ClickCheckbox               I have a bike               on
    ${found}=                   IsText                      Last name:
    Should Be Equal             ${found}                    ${TRUE}

IsNoText in different frame
    [Tags]                      istext
    ClickCheckbox               I have a bike               on
    ${notfound}=                IsNoText                    Last name:                  0.1s
    Should Be Equal             ${notfound}                 ${FALSE}

Upload files with index
    [Tags]                      Frame    Upload
    UploadFile                  1                           test1.txt
    ExecuteJavaScript           return document.querySelector('#myFile1').value         $value
    ShouldBeEqual               ${value}                    C:\fakepath\test1.txt
    UploadFile                  2                           test2.txt
    ExecuteJavaScript           return document.querySelector('#myFile2').value         $value
    ShouldBeEqual               ${value}                    C:\fakepath\test2.txt

Upload files with locator
    [Tags]                      Frame    Upload
    UploadFile                  Uploadme                    test1.txt
    ExecuteJavaScript           return document.querySelector('#myFile1').value         $value
    ShouldBeEqual               ${value}                    C:\fakepath\test1.txt

Upload with xpath
    [Tags]                      Frame    Upload
    UploadFile                  //*[@id\='myFile3']         test2.txt
    ExecuteJavaScript           return document.querySelector('#myFile3').value         $value
    ShouldBeEqual               ${value}                    C:\fakepath\test2.txt

GetTextCount and VerifyTextCount from multiple frames
    [Tags]                      Frame
    ${count}=                   GetTextCount    text
    Should Be Equal As Numbers  ${count}        15
    VerifyTextCount             Text            7
    
GetWebelement from multiple frames
    [Tags]                      Frame
    ${elems}=                   GetWebElement    //button    all_frames=False
    ${count_one_frame}=         Evaluate         len($elems)
    ${elems}=                   GetWebElement    //button
    ${count_all_frames}=         Evaluate         len($elems)
    Should Be Equal As Numbers  ${count_one_frame}         1
    Should Be Equal As Numbers  ${count_all_frames}        7


GetWebelement & GetAttribute from multiple frames with element type
    [Tags]                      Frame    Get
    # Without all_frames
    ${elem1}=                    GetWebElement    Blue     element_type=item    tag=input
    ${attr1}=                    GetAttribute     Blue     id    element_type=item    tag=input
    ${elem2}=                    GetWebElement    Button1  element_type=text
    ${attr2}=                    GetAttribute     skimClick disable button  id    element_type=text
    ShouldBeEqual                ${attr1}         ch_1_1
    ShouldBeEqual                ${attr2}         skimclick
    
    # With all_frames, note that all_frames is not even supported in GetAttribute
    ${elem1}=                    GetWebElement    Blue     element_type=item    tag=input    all_frames=True
    ${attr1}=                    GetAttribute     Blue     id    element_type=item    tag=input      all_frames=True
    ${elem2}=                    GetWebElement    Button1  element_type=text    all_frames=True
    ${attr2}=                    GetAttribute     skimClick disable button  id    element_type=text  all_frames=True
    ShouldBeEqual                ${attr1}         ch_1_1
    ShouldBeEqual                ${attr2}         skimclick
