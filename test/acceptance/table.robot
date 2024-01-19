*** Settings ***
Documentation    Tests for table keywords
Library          QWeb
Library          Collections
Suite Setup      OpenBrowser    file://${CURDIR}/../resources/table.html  ${BROWSER}  --headless      
Suite Teardown   CloseBrowser
Test Timeout     60 seconds

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

Get specific Column header
    UseTable                Sample
    ${value}=               GetColumn              3
    Should Be Equal         ${value}               Age

Get All columns to list
    UseTable                Sample
    ${all}=                 GetColumn
    ${length}=              Get Length       ${all}
    Should Be Equal As Integers    ${length}    4
    List Should Contain Value      ${all}       Date
    Log List   ${all}

Get Column errors
    UseTable                Sample
    # Value differs
    ${value}=               GetColumn              3
    Should Not Be Equal     ${value}               Date
    # too low index
    Run Keyword And Expect Error    QWebValueError:*    GetColumn            -1
    # index larger than column count
    Run Keyword And Expect Error    QWebValueError: Column index out of range*   
    ...                             GetColumn            88
    # index not a number
    Run Keyword And Expect Error    ValueError*   
    ...                             GetColumn            abc
    # index is number but not int
    Run Keyword And Expect Error    ValueError*
    ...                             GetColumn              3.8  


VerifyColumn value positive
    UseTable                Sample
    # Column must exist in specific index
    VerifyColumn            Age    3
    # Column exists at any position
    VerifyColumn            Date
    # Column exists, 0 given as index
    VerifyColumn            Date   0   
    # partial match on
    VerifyColumn            name   2    partial_match=True
    VerifyColumn            First       partial_match=True
    VerifyColumn            Firstname   partial_match=False


    

VerifyColumn value errors
    UseTable                Sample
    # too low index
    Run Keyword And Expect Error    QWebValueError:*    VerifyColumn            Age    -1
    # index larger than column count
    Run Keyword And Expect Error    QWebValueError: Column index out of range*   
    ...                             VerifyColumn            Age    88
    # not matching expected
    Run Keyword And Expect Error    QWebElementNotFoundError:*   VerifyColumn         Age    2           
    # Column does not exist at any position
    Run Keyword And Expect Error    QWebElementNotFoundError:*   VerifyColumn         Not Here
    # index not numeric
    Run Keyword And Expect Error    ValueError:*   VerifyColumn         Age    Age
    # index not int
    Run Keyword And Expect Error    ValueError:*   VerifyColumn         Age    3.99 
    # column exists but partial_match is False
    Run Keyword And Expect Error    QWebElementNotFoundError*
    ...                             VerifyColumn            First       partial_match=False
    # column exists at index but partial_match is False
    Run Keyword And Expect Error    QWebElementNotFoundError*
    ...                             VerifyColumn            First   1   partial_match=False

Column count
    UseTable                Sample
    ${amount}               GetColumnCount
    Should Be Equal As Integers         ${amount}             4
    UseTable                CheckBox
    ${amount2}               GetColumnCount
    Should Be Equal As Integers         ${amount2}            2