*** Settings ***
Documentation       Test for pdf keywords. Browser needs to be open for Linux pipeline(screenshot err)
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}  --headless
Suite Teardown      CloseBrowser
Test Timeout        1min

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Use pdf file verify and verify no text
    UsePdf              dummy.pdf
    VerifyPdfText       Simple PDF File
    VerifyNoPdfText     FooBar

Use text file verify and verify no text
    UseFile             test3.txt
    VerifyPdfText       Lorem ipsum dolor sit amet
    VerifyNoPdfText     FooBar

GetPdfText - substring using between parameter
    UsePdf              dummy.pdf
    ${text}             GetPdfText     between=Simple???File
    ShouldBeEqual       ${text}        PDF
    ${text}             GetPdfText     between=Lorem???dolor
    ShouldBeEqual       ${text}        ipsum
    ${text}             GetPdfText     between=Qentinel???Robot  include_locator=True
    ShouldBeEqual       ${text}        Qentinel Test Automation
    ${text}             GetPdfText     between=Qentinel???Robot
    ShouldBeEqual       ${text}        Test Automation
    ${text}             GetPdfText     between=Qentinel???Automation    exclude_post=False
    ShouldBeEqual       ${text}        Test Automation
    ${text}             GetPdfText     between=7???10
    ShouldBeEqual       ${text}        PDF

GetFileText - substring using between parameter
    UseFile             test3.txt
    ${text}             GetFileText    between=Aliquam in eu???at integer
    ShouldBeEqual       ${text}        lorem

GetPdfText - substring using from start and from end parameters
    UsePdf              dummy.pdf
    ${text}             GetPdfText      from_start=6
    ShouldBeEqual       ${text}         Simple
    ${text}             GetPdfText      from_end=6
    ShouldBeEqual       ${text}         Robot
    ${text}             GetPdfText      between=ipsum???    from_start=6
    ShouldBeEqual       ${text}         dolor
    ${text}             GetPdfText      between=???dolor    from_end=6
    ShouldBeEqual       ${text}         ipsum

GetFileText - substring using from start and from end parameters
    UseFile             test3.txt
    ${text}             GetFileText      from_start=11
    log to console      ${text}
    ShouldBeEqual       ${text}          Lorem ipsum
    ${text}             GetFileText      from_end=6
    ShouldBeEqual       ${text}          ibero.
    ${text}             GetFileText      between=ipsum???    from_start=6
    ShouldBeEqual       ${text}          dolor
    ${text}             GetFileText      between=???dolor    from_end=6
    ShouldBeEqual       ${text}          ipsum

Use pdf file - negative cases
    ${message}=     Set Variable    QWebFileNotFoundError: File not found*
    Run Keyword and Expect Error   ${message}    UsePdf             FooBar
    UsePdf          dummy.pdf
    ${message}=     Set Variable    QWebValueMismatchError: File did not contain the text*
    Run Keyword and Expect Error   ${message}    VerifyPdfText      FooBar
    Run Keyword and Expect Error   ${message}    GetPdfText         between=FooBar???
    ${message}=     Set Variable    QWebUnexpectedConditionError: Text PDF exists in pdf file*
    Run Keyword and Expect Error   ${message}    VerifyNoPdfText    PDF

Use text file - negative cases
    ${message}=     Set Variable    QWebFileNotFoundError: File not found*
    Run Keyword and Expect Error   ${message}    UseFile             FooBar
    UseFile         test3.txt
    ${message}=     Set Variable    QWebValueMismatchError: File did not contain the text*
    Run Keyword and Expect Error   ${message}    VerifyFileText      FooBar
    Run Keyword and Expect Error   ${message}    GetFileText         between=FooBar???
    ${message}=     Set Variable    QWebUnexpectedConditionError: Text lorem exists in file*
    Run Keyword and Expect Error   ${message}    VerifyNoFileText    lorem

verifyfile
    [tags]          verify
    VerifyFile      test3.txt
    VerifyFile      dummy.pdf
    VerifyFile      infinity.png

Multiline pdf text
    [tags]          verify  normalize
    UsePdf              sample-pdf-file.pdf
    Run Keyword And Expect Error    QWebValueMismatchError:*      VerifyPdfText       Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book
    VerifyPdfText       Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book   normalize=True
