*** Settings ***
Documentation     Tests for Drag and Drop keyword
Library           QWeb
Suite Setup       OpenBrowser    file://${CURDIR}/../resources/drag.html    ${BROWSER}
Suite Teardown    CloseBrowser
Test Setup        SetConfig       WindowSize    1920x1080
Test Timeout      60 seconds
Test Teardown     Refresh Page

*** Variables ***
${BROWSER}    chrome

${childnodes}    ${EMPTY}
${childnodes2}    ${EMPTY}
${text}    ${EMPTY}

*** Test Cases ***
Drag and Drop all elements to box
    [tags]              PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX  PROBLEM_IN_EDGE    RESOLUTION_DEPENDENCY
    VerifyText          Put element to this div
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '0'
    DragDrop            Qentinel            Put element to this div
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '1'
    DragDrop            Draggable Text      Put element to this div
    DragDrop            Smaller text        Put element to this div
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '3'

Drag and Drop use xpath locator
    [tags]              PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX  PROBLEM_IN_EDGE    RESOLUTION_DEPENDENCY
    VerifyText          Put element to this div
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '0'
    DragDrop            //*[@id\='drag1']   //*[@id\='div1']
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '1'

Drag and Drop use index locator
    [tags]              PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX  PROBLEM_IN_EDGE    RESOLUTION_DEPENDENCY
    VerifyText          Put element to this div
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '0'
    DragDrop            index        Put element to this div    index=3
    ExecuteJavaScript   return document.querySelector('#div1').textContent        $text
    ShouldContain       ${text}             Smaller text

Drag and Drop draggable not found
    Run Keyword And Expect Error    QWebElementNotFoundError: Unable to find element for*
    ...     DragDrop            Foo         Bar     timeout=2

Drag further in screen
    [tags]              PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX  PROBLEM_IN_EDGE    RESOLUTION_DEPENDENCY
    ScrollText          Page ends here
    VerifyText          Put element to this box
    ExecuteJavaScript   return document.getElementById('div2').childElementCount  $childnodes2
    ShouldBeEqual       '${childnodes2}'     '0'
    DragDrop            Qbox                 Put element to this box
    ExecuteJavaScript   return document.getElementById('div2').childElementCount  $childnodes2
    ShouldBeEqual       '${childnodes2}'     '1'
    DragDrop            Draagable Text       Put element to this box
    DragDrop            Smaaaller text       Put element to this box
    ExecuteJavaScript   return document.getElementById('div2').childElementCount  $childnodes2
    ShouldBeEqual       '${childnodes2}'     '3'

DragVelocity
    [tags]              PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX  PROBLEM_IN_EDGE    RESOLUTION_DEPENDENCY
    ScrollText          Drag the W3Schools image into the rectangle:
    VerifyText          Put element to this div
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '0'
    DragDrop            Qentinel            Put element to this div    dragtime=1s
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '1'

Offset
    [tags]              PROBLEM_IN_WINDOWS	PROBLEM_IN_FIREFOX  PROBLEM_IN_EDGE    RESOLUTION_DEPENDENCY
    VerifyText          Put element to this div
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '0'
    DragDrop            Qentinel            Put element to this div    right=30
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '1'
    DragDrop            Draggable Text      Put element to this div    above=20
    DragDrop            Smaller text        Put element to this div    left=30
    ExecuteJavaScript   return document.getElementById('div1').childElementCount  $childnodes
    ShouldBeEqual       '${childnodes}'     '3'
