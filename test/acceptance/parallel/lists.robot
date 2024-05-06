*** Settings ***
Documentation    Tests for table keywords
Library          QWeb
Library          Collections
Suite Setup      OpenBrowser  http://127.0.0.1:8000/lists.html  ${BROWSER}  --headless
Suite Teardown   CloseBrowser
Test Timeout     60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Use list get element by xpath
    UseList                 boxes           selector=class
    ${list}                 GetList
    Log                     ${list}
    VerifyLength            4
    VerifyList              Box 2           2
    #Another way to write xpath:
    UseList                 //*[@class\="boxes"]
    VerifyLength            4

Use list get element by text
    UseList                 Robot testing
    ${list1}                GetList
    VerifyLength            7
    UseList                 Qentinel
    ${list2}                GetList
    ListShouldContainSubList    ${list1}    ${list2}
    VerifyLength            4
    VerifyList              Qentinel        1
    VerifyList              QMobile         4
    VerifyList              QVision
    VerifyNoList            Kalakalle

GetList substring
     UseList                 Qentinel
    ${text}                 GetList         1   between=Q???l
    ShouldBeEqual           ${text}         entine

UseList and get errors
    UseList                 Robot testing
    ${err}                          Set Variable    QWebValueMismatchError: Expected length*
    Run Keyword and Expect Error   ${err}    VerifyLength       6
    ${err}                          Set Variable    QWebElementNotFoundError: Unable*
    Run Keyword and Expect Error   ${err}     UseList           Kalakalle       timeout=2
    ${err}                          Set Variable    QWebValueError: Index can't be bigger than*
    Run Keyword and Expect Error   ${err}     VerifyList   Qentinel   index=10  timeout=2

UseList get element with parent
    UseList    QVision    parent=ul
    ${list}                 GetList
    Log                     ${list}
    VerifyLength            7
    VerifyList    Text in outer list    1
    VerifyList    QWeb    4

UseList from divs with parent
    UseList    Inner box 1    parent=.boxes
    ${list}                 GetList
    Log                     ${list}
    VerifyLength    4
    VerifyList    Box 2    2

UseList get element with child
    UseList    Robot testing    child=ul
    ${list}                 GetList
    Log                     ${list}
    VerifyLength    4
    VerifyList    Qentinel    1
    VerifyList    QMobile    4

UseList from divs with child
    UseList    Box 1    child=.innerBox1
    ${list}                 GetList
    Log                     ${list}
    VerifyLength    1
    VerifyList    Inner box 1    1

Uselist xpath and parent
    UseList    innerBox1    selector=class    parent=.boxes
    ${list}    GetList
    Log    ${list}
    VerifyLength            4
    VerifyList              Box 2           2

Uselist with child and expect error
    ${err}                          Set Variable    QWebElementNotFoundError: Unable*
    # jailed due to Chrome 123 bug
    #Run Keyword And Expect Error   ${err}    UseList    innerBox1    selector=class    child=.boxes
    Run Keyword And Expect Error   ${err}    UseList    Robot Testing    child=ol
    #Run Keyword And Expect Error   ${err}    Uselist    Inner Box 1    child=.boxes

Click list element from divs
    UseList                 boxes    selector=class
    ClickList    1
    VerifyText              parentbox clicked!
    ClickList    1          tag=div
    VerifyText              childbox1 clicked!

Click list with nested list element
    UseList                 Robot testing
    ClickList    2
    VerifyText              Robot clicked!

Click list element
    UseList                 QWeb
    ClickList    4
    VerifyText              QMobile clicked

Click list element with only one element in list
    UseList                 innerBox1   selector=class
    ClickList   1
    VerifyText              childbox1 clicked!
    ClickList   1           tag=div
    VerifyText              childbox2 clicked!
