*** Settings ***
Documentation                   Tests for Dropdown keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 file://${CURDIR}/../resources/dropdown.html            ${BROWSER}
Suite Teardown                  CloseBrowser
Test Timeout                    1min

*** Variables ***
${BROWSER}                      chrome

*** Test Cases ***
Test Dropdown Keyword With Xpath
    ${foo}=                     GetDropDownValues           xpath\=//*[@id\="dropdown1"]
    Should Be Equal             '${foo}'                    '['test1', 'test2', 'test3', 'test4']'

    VerifyNoOption              xpath\=//*[@id\="dropdown1"]                            test5

    DropDown                    xpath\=//*[@id\="dropdown1"]                            test4
    VerifyText                  Dropdown1-test4

    DropDown                    xpath\=//*[@id\="dropdown1"]                            test2
    VerifyText                  Dropdown1-test2

    DropDown                    xpath\=//*[@id\="dropdown1"]                            test1
    VerifyText                  Dropdown1-test1

    DropDown                    xpath\=//*[@id\="dropdown1"]                            test3
    VerifyText                  Dropdown1-test3

Test Dropdown Keyword With Text
    ${foo}=                     GetDropDownValues           test1
    Should Be Equal             '${foo}'                    '['test1', 'test2', 'test3', 'test4']'

    VerifyNoOption              test1                       test5

    DropDown                    Dropdown2                   test2.4
    VerifyText                  Dropdown2-test2.4

    DropDown                    Dropdown2                   test2.2
    VerifyText                  Dropdown2-test2.2

    DropDown                    Dropdown2                   test2.1
    VerifyText                  Dropdown2-test2.1

    DropDown                    Dropdown2                   test2.3
    VerifyText                  Dropdown2-test2.3

Test Dropdown Keyword With Value
    [Documentation]             Tests choosing dropdown with value instead of text, with CSSSelectors on
    ...                         and off.
    VerifyNotext                bear
    Dropdown                    Joulupukki                  bear
    VerifyText                  bear
    VerifyNoText                boar
    DropDown                    Joulupukki                  boar
    VerifyText                  boar
    VerifyNotext                dog
    DropDown                    Joulupukki                  dog
    VerifyText                  dog
    VerifyNoText                cat
    DropDown                    Joulupukki                  cat
    VerifyText                  cat

Test Dropdown Keyword With Index
    [Documentation]             Tests choosing dropdown with index, with CSSSelectors on and off.
    VerifyNotext                bear
    Dropdown                    Joulupukki                  [[3]]
    VerifyText                  bear
    VerifyNoText                boar
    DropDown                    Joulupukki                  [[2]]
    VerifyText                  boar
    VerifyNotext                dog
    DropDown                    Joulupukki                  [[1]]
    VerifyText                  dog
    VerifyNoText                cat
    DropDown                    Joulupukki                  [[0]]
    VerifyText                  cat

Find Dropdowns by Text
    Dropdown                    Kolmas                      Bar
    VerifyText                  Dropdown3-Bar
    ${foo}=                     GetDropDownValues           Kolmas

Find Dropdowns by Text And Anchor
    Dropdown                    Kolmas                      Rules                       avulla
    VerifyText                  Dropdown4-Rules
    VerifySelectedOption        Kolmas                      Rules                       avulla

Find Dropdowns by CSS label for
    Dropdown                    label with                  Rules
    VerifySelectedOption        label with                  Rules

Find Dropdowns by CSS label without for
    [tags]                      PROBLEM_IN_FIREFOX
    Dropdown                    label without               Rules
    VerifyOption                label without               Rules
    VerifyNoOption              label without               Ruless
    VerifyOption                label without               OK
    VerifyOption                label without               Qentinel

Delayed Dropdown
    ClickText                   Show dropdown
    Dropdown                    hidden:                     Oslo
    VerifySelectedOption        hidden:                     Oslo
    VerifyText                  Dropdown7-Rules

Get Selected values from dropdowns
    [tags]                      PROBLEM_IN_FIREFOX
    Dropdown                    label with                  Rules
    Dropdown                    label without               Qentinel
    ${FIRST}                    GetSelected                 label without
    ${SECOND}                   GetSelected                 label with
    ShouldBeEqual               ${FIRST}                    Qentinel
    ShouldBeEqual               ${SECOND}                   Rules

Dropdown Text not found
    Run Keyword And Expect Error                            QWebElementNotFoundError: Unable to find element*
    ...                         Dropdown                    nothere                     notfound                   1                0.1s

    Run Keyword And Expect Error                            QWebValueError: Option "notfound" is not in the options list.*
    ...                         Dropdown                    Dropdown2                   notfound                   1                0.1s

    Run Keyword And Expect Error                            QWebElementNotFoundError: Unable to find element*
    ...                         DropDown                    xpath\=//*[@id\="dropdown99"]                          qwerty           1       0.1s

    Run Keyword And Expect Error                            QWebValueError: Option "qwerty" is not in the options list.*
    ...                         DropDown                    xpath\=//*[@id\="dropdown1"]                           qwerty           1       0.1s

Dropdown with same locator than other dropdown option
    [tags]                      PROBLEM_IN_FIREFOX
    Dropdown                    Typex                       Flow
    SetConfig                   CssSelectors                off
    run keyword and expect error                            QWebValueError: Option "optionx" is not in the options list*
    ...                         Dropdown                    Flow                        optionx                    timeout=1
    SetConfig                   CssSelectors                on
    Dropdown                    ffffff                      abcd
    Dropdown                    Flow                        optionx
    VerifyText                  Dropdown9-optionx

Test dd kw:s when traverse limit is false
    [documentation]             Find input from overly nested dom.
    [tags]                      limit_traverse
    VerifySelectedOption        Foobar                      Foo                         limit_traverse=False
    Dropdown                    Foobar                      Bar                         limit_traverse=False
    VerifySelectedOption        Foobar                      Bar                         limit_traverse=False

Locate dropdowns with anchor
    [Documentation]             Locator is the default option of the dropdown and anchor is a number
    Dropdown                    Qentinel                    Rules                       anchor=3
    VerifyInputValue            //*[@id\="dropdown6"]       Rules
    RefreshPage
    DropDown                    Qentinel                    Rules                       anchor=2
    VerifyInputValue            //*[@id\="dropdown5"]       Rules

Locate dropdowns with anchor 2
    [Documentation]             Locator is the default option of the dropdown and anchor is text
    RefreshPage
    DropDown                    Qentinel                    Rules                       anchor=Ankkurien avulla
    VerifyInputValue            //*[@id\="dropdown4"]       Rules
    RefreshPage
    DropDown                    Qentinel                    Rules                       anchor=Delayed dropdown
    VerifyInputValue            //*[@id\="dropdown6"]       Rules

Select and unselect in multiselection dropdown
    [Documentation]             Test for multiple selection dropdowns
    RefreshPage
    DropDown                    Choose a spacecraft         USS Defiant
    DropDown                    Choose a spacecraft         Scimitar
    DropDown                    Choose a spacecraft         Galileo
    VerifySelectedOption        Choose a spacecraft         Scimitar
    ${selected}=                GetSelected                 Choose a spacecraft
    Should Contain              ${selected}                 Galileo                     USS Defiant                Scimitar
    DropDown                    Choose a spacecraft         Scimitar                    unselect=True
    ${selected}=                GetSelected                 Choose a spacecraft
    Should Not Contain          ${selected}                 Scimitar

Unselect on single selection dropdown
    Select and unselect in multiselection dropdown
    [Documentation]             Test that error is raised when unselect is used with single select dropdown
    RefreshPage
    Dropdown                    label with                  Rules
    Run Keyword And Expect Error                            *You may only deselect options of a multi-select*
    ...                         Dropdown                    label with                  Rules                      unselect=True


