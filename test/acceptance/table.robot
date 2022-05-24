*** Settings ***
Documentation    Tests for table keywords
Library          QWeb
Suite Setup      OpenBrowser    file://${CURDIR}/../resources/table.html  ${BROWSER}  --headless      
Suite Teardown   CloseBrowser
Test Timeout     10 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
# Jailed test due to random failures in pipeline
#Verify No Table Defined
#    Run Keyword And Expect Error
#...    ValueError: Table has not been defined with UseTable keyword    VerifyTable     r2c1        Jill

Verify Value by coordinates
    UseTable                Sample
    VerifyTable             r2c1                    Jill
    VerifyTable             r2c3                    ${EMPTY}
    VerifyTable             r2c4                    2017*
    VerifyTable             r2c4                    2017-??-12
    TypeText                r4c1                    Qentiro

Verify Value Negative Cases
    UseTable                Sample
    Run Keyword And Expect Error       QWebValueError*   VerifyTable   r2c1       Foo  timeout=1

Type text to table and verify values
    [Timeout]               30 seconds
    UseTable                Sample
    TypeText                r4c1                    Qentiro
    TypeText                r4c2                    Robot
    TypeText                r4c3                    17
    TypeText                r4c4                    2019-02-24
    VerifyInputValue        r4c1                    Qentiro
    VerifyInputValue        r4c2                    Robot
    VerifyInputValue        r4c3                    17
    VerifyInputValue        r4c4                    2019-02-24
    Run Keyword And Expect Error       QWebValueError: Expected value "2019-02-23" didn't*
    ...   VerifyInputValue              r4c4        2019-02-23          timeout=1

Get Cell Value to variable
    [Timeout]               30 seconds 
    UseTable                Sample
    ${TEST}                 GetCellText             r2c3
    ShouldBeEqual           ${TEST}                 ${EMPTY}
    TypeText                r4c3                    Save me for later use
    ${TEST}                 GetInputValue           r4c3
    ShouldBeEqual           ${TEST}                 Save me for later use
    ${TEST}                 GetCellText             r2c1
    ShouldBeEqual           ${TEST}                 Jill
    TypeText                r5c1                    8446543
    ${VALUE}                GetInputValue           r5c1
    ${TEXT}                 GetCellText             r5c1
    ShouldBeEqual           ${VALUE}                8446543
    ShouldBeEqual           ${TEXT}                 Some text inside of cell
    ClickCell               r5c2
    VerifyText              checkbox true
    ClickCell               r5c2
    VerifyText              checkbox false
    ClickCell               r5c3
    VerifyText              radio true
    VerifyText              checkbox
    SetConfig               CSSSelectors            On
    UseTable                Jackson
    VerifyTable             r3c2                    Jack*
    Run Keyword And Expect Error       QWebElementNotFoundError: Unable to find element*
    ...   GetInputValue     r2c1   timeout=1
    Run Keyword And Expect Error       QWebElementNotFoundError: Unable to find element*   GetCellText   r4c5   timeout=1

Row count
    UseTable                Sample
    ${amount}               GetTableRow             //last
    Should Be Equal         '${amount}'             '5'
    # exluding headers:
    ${content}              GetTableRow             //last      skip_header=True
    Should Be Equal         '${content}'            '4'
