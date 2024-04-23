*** Settings ***
Documentation     More tests for table keywords
Library           QWeb
Suite Setup       OpenBrowser  file://${CURDIR}/../../resources/table2.html  ${BROWSER}  --headless
Suite Teardown    CloseBrowser
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome
${value}      ${EMPTY}

*** Test Cases ***
Use table kw:s with text locator
    SetConfig               CSSSelectors            on
    UseTable                Sample
    VerifyTable             r?Jill/c?Firstname     Jill
    VerifyTable             r?Eve/c?Lastname       Jackson
    UseTable                Stars
    VerifyTable             r?Jimi/c?Age           27
    VerifyTable             r?Buddy/c?Date         1959-02-03
    HoverText               Text Node              # make bottom elements visible - Safari
    UseTable                Qentiro
    DropDown                r?Qentiro/c?Some       Ruotsi
    VerifySelectedOption    r2c5                   Ruotsi
    TypeText                r1/c?Qentiro           Qentinel
    VerifyInputValue        r?Helsinki/c2          Qentinel
    RefreshPage

Use table kw:s with xpath locators
    SetConfig               CSSSelectors            on
    UseTable                /html/body/table[1]
    VerifyTable             r?Jill/c?Firstname     Jill
    VerifyTable             r?Eve/c?Lastname       Jackson
    UseTable                Stars
    VerifyTable             r?Jimi/c?Age           27
    VerifyTable             r?Buddy/c?Date         1959-02-03
    HoverText               Text Node              # make bottom elements visible - Safari
    UseTable                Qentiro
    DropDown                r?Qentiro/c?Some       Ruotsi
    VerifySelectedOption    r2c5                   Ruotsi
    TypeText                r1/c?Qentiro           Qentinel
    VerifyInputValue        r?Helsinki/c2          Qentinel
    RefreshPage
    UseTable                xpath\=/html/body/table[1]
    VerifyTable             r?Jill/c?Firstname     Jill
    VerifyTable             r?Eve/c?Lastname       Jackson
    UseTable                Stars
    VerifyTable             r?Jimi/c?Age           27
    VerifyTable             r?Buddy/c?Date         1959-02-03
    UseTable                Qentiro
    DropDown                r?Qentiro/c?Some       Ruotsi
    VerifySelectedOption    r2c5                   Ruotsi
    TypeText                r1/c?Qentiro           Qentinel
    VerifyInputValue        r?Helsinki/c2          Qentinel
    RefreshPage
    UseTable                //table[contains(.,"Sample")]
    VerifyTable             r?Jill/c?Firstname     Jill
    VerifyTable             r?Eve/c?Lastname       Jackson
    UseTable                Stars
    VerifyTable             r?Jimi/c?Age           27
    VerifyTable             r?Buddy/c?Date         1959-02-03
    UseTable                Qentiro
    DropDown                r?Qentiro/c?Some       Ruotsi
    VerifySelectedOption    r2c5                   Ruotsi
    TypeText                r1/c?Qentiro           Qentinel
    VerifyInputValue        r?Helsinki/c2          Qentinel
    RefreshPage

Verify Multiple
    UseTable                Sample
    VerifyTable             r2c1                    Jill
    VerifyTable             r2c4                    2017*
    UseTable                Stars
    VerifyTable             r2c1                    Jimi
    VerifyTable             r2c4                    1970*

Use general kw:s with Table using cell coordinates as an locator
    [Tags]
    SetConfig               CSSSelectors            on
    HoverText               Text Node              # make bottom elements visible - Safari
    UseTable                Qentiro
    TypeText                r1c2                    Test Automation
    VerifyInputValue        r1c2                    Test Automation
    TypeText                r1c3                    Robot
    VerifyInputValue        r1c3                    Robot
    DropDown                r1c4                    Vantaa
    DropDown                r1c5                    Ruotsi
    DropDown                r1c6                    Yes
    DropDown                r2c6                    No
    ClickCheckBox           r3c3                    On
    VerifyCheckBoxValue     r3c3                    On
    ClickCheckBox           r3c3                    Off
    ${foo}=                 GetDropDownValues         r1c4
    Should Be Equal         '${foo}'    '['Helsinki', 'Espoo', 'Vantaa', 'Juupajoki']'
    VerifyNoOption          r1c4                    Vaasa
    DropDown                r2c5                    Turku
    DropDown                r2c4                    Espoo
    DropDown                r2c4                    Juupajoki
    DropDown                r2c5                    Norja

Use general kws with Table Get row by text or start counting from last cell
    [Tags]
    SetConfig               PartialMatch            False
    HoverText               Text Node              # make bottom elements visible - Safari
    UseTable                Robot
    ClickCheckBox           r?Qentiro/c1            On
    VerifyCheckBoxValue     r2c1                    On
    VerifyCheckBoxValue     r3c1                    Off
    ClickCheckBox           r?Qentiro/c1            On                      2
    VerifyCheckBoxValue     r3c1                    On
    ClickCheckBox           r?Qentiro/c1            Off                     Robot
    VerifyCheckBoxValue     r2c1                    Off
    VerifyCheckBoxValue     r?Some/c3               Off
    ClickCheckBox           r3c3                    On
    VerifyCheckBoxValue     r?Some/c3               On
    TypeText                r3c4                    Cell 4 in row 3!
    DropDown                r?Random/c1             Norja
    VerifySelectedOption    r-2c1                   Norja
    ClickCell               r?Text Node/c6
    ExecuteJavascript       window.scrollTo(0, document.body.scrollHeight);    # scroll to bottom, safari needs this
    DropDown                r-1c2                   Robot
    VerifySelectedOption    r6c2                    Robot
    ClickCell               r-1c6

Anchors and indexes
    HoverText               Text Node              # make bottom elements visible - Safari
    UseTable                Text Node
    #Using index anchor(2)
    ClickCell               r?Text/c6               2
    TypeText                r?Added/c3              Located by text Added
    TypeText                r-1c3                   Last index, cell 3
    TypeText                r-2c4                   Second to last, cell 4
    #Using text anchor (Node)
    ClickCell               r?Text/c6               Node
    TypeText                r-1c3                   c3 ind\=1
    #Using index to point second input from cell(2)
    TypeText                r-1c3                   c3 ind\=2               index=2
    TypeText                r-1c4                   c4 ind\=1
    TypeText                r-1c4                   c4 ind\=2               index=2
    DropDown                r-1c5                   Qentinel
    DropDown                r-1c5                   Robot                   index=2
    ClickCheckbox           r-1c6                   On
    VerifyCheckBoxValue     r-1c6                   On
    ClickCheckbox           r-2c6                   On                      index=2
    VerifyCheckBoxValue     r-2c6                   On                      index=2
    ClickCheckbox           r-3c6                   On
    DropDown                r-2c5                   Robot
    VerifySelectedOption    r-2c5                   Robot
    DropDown                r-2c5                   Qentinel                index=2
    VerifySelectedOption    r-2c5                   Qentinel                index=2
    DropDown                r-3c5                   Qentinel
    DropDown                r-3c5                   Robot                   index=2
    TypeText                r-3c3                   c3 ind\=1
    TypeText                r-2c3                   c3 ind\=2               index=2
    TypeText                r-3c4                   c4 ind\=1
    TypeText                r-3c4                   c4 ind\=2               index=2
    TypeText                r-2c3                   c3 ind\=1
    TypeText                r-3c3                   c3 ind\=2               index=2
    TypeText                r-2c4                   c4 ind\=1
    TypeText                r-2c4                   c4 ind\=2               index=2
    ClickCheckbox           r-3c2                   On
    ClickCheckbox           r-2c2                   On
    ClickCheckbox           r-1c2                   On
    DropDown                r-2c2                   Qentinel
    DropDown                r-1c2                   Robot
    ClickCell               r?Text/c6               Node
    ExecuteJavascript       window.scrollTo(0, document.body.scrollHeight);    # scroll to bottom, safari needs this
    DropDown                r-1c2                   Robot
    ClickCheckbox           r-1c2                   On
    TypeText                r-1c3                   new ind\=1
    TypeText                r-1c3                   new ind\=2              index=2
    TypeText                r-1c4                   new ind\=1
    TypeText                r-1c4                   new ind\=2              index=2
    DropDown                r-1c5                   Robot
    DropDown                r-1c5                   Qentinel                index=2
    ClickCheckbox           r-1c6                   On                      index=2
    VerifyCheckBoxValue     r-1c6                   On                      index=2

Using Cells, starts from last one
    UseTable                Some Text
    ClickCheckbox           r-1c-1                  On
    ClickCheckbox           r-1c-1                  Off                     index=2
    ClickCheckbox           r-2c-1                  Off
    ClickCheckbox           r-2c-1                  On                      index=2
    ClickCheckbox           r-3c-1                  On
    ClickCheckbox           r-3c-1                  Off                     index=2
    DropDown                r-1c-2                  Qentinel
    VerifySelectedOption    r-1c-2                  Qentinel
    DropDown                r-1c-2                  Robot                   index=2
    VerifySelectedOption    r-1c-2                  Robot                   index=2
    TypeText                r-1c-3                  -3 ind\=2               index=2
    TypeText                r-1c-3                  -3 ind\=1
    TypeText                r-1c-4                  -4 ind\=2               index=2
    TypeText                r-1c-4                  -4 ind\=1

Get row index and cell values to variables
    [Tags]
    SetConfig               CSSSelectors            True
    UseTable                Some Text
    ${row1}                 GetTableRow             //last
    ${row2}                 GetTableRow             Text
    #with anchor:
    ${row3}                 GetTableRow             Text                    Node
    Should Be Equal         '${row1}'               '9'
    Should Be Equal         '${row2}'               '3'
    Should Be Equal         '${row3}'               '5'
    ${value}                GetInputValue           r-1c3
    Should Be Equal         ${value}                -4 ind\=1

Upload element inside of table cell
    UseTable                Qentiro
    UploadFile              r?Random/c3             test1.txt
    ExecuteJavaScript       return document.querySelector('#myFile1').value   $value
    ShouldBeEqual           ${value}                C:\fakepath\test1.txt

Use Parent table
    [tags]                  parent
    SetConfig               CSSSelectors            on
    SetConfig               PartialMatch            True
    UseTable                Qentiro                 parent=True
    VerifyTable             r?one/c?text            Robot Automation
    VerifyTable             r?two/c?text            Qentinel
    TypeText                r?two/c?input           Leppävaara office
    VerifyInputValue        r3c3                    Leppävaara office
    Dropdown                r?one/c?dd              baz
    VerifySelectedOption    r2c4                    baz

Use child table
    [tags]                  child
    SetConfig               CSSSelectors            on
    UseTable                Qentiro                 child=True
    VerifyTable             r1c1                    Some text inside of child

Get first empty row
    [tags]                  empty
    UseTable                Stars
    TypeText                r?EMPTY/c?First         Qentsu
    TypeText                r?EMPTY/c?Last          Robot
    TypeText                r?EMPTY/c?Age           19
    TypeText                r?EMPTY/c?Date          2000-01-01
    VerifyInputValue        r?EMPTY/c?First         Qentsu
    VerifyInputValue        r?EMPTY/c?Last          Robot
    VerifyInputValue        r?EMPTY/c?Age           19
    VerifyInputValue        r?EMPTY/c?Date          2000-01-01
    SetConfig               PartialMatch            True

Multiple clickable elements inside a cell
    UseTable                Leijonat
    ClickCell               r?Olli/c3               index=2    tag=input
    VerifyCheckboxValue     r?Olli/c3               off        index=1
    VerifyCheckboxValue     r?Olli/c3               on         index=2
    VerifyCheckboxValue     r?Olli/c3               off        index=3
    ClickCell               r?Jussi/c3              index=1    tag=input
    VerifyCheckboxValue     r?Jussi/c3              on         index=1
    ClickCell               r?Jussi/c3              index=1    tag=input
    ClickCell               r?Jussi/c3              index=3    tag=input
    VerifyCheckboxValue     r?Jussi/c3              off        index=1
    VerifyCheckboxValue     r?Jussi/c3              off        index=2
    VerifyCheckboxValue     r?Jussi/c3              on         index=3
