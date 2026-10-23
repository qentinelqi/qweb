*** Settings ***
Documentation     Tests for UploadFile keyword
Library           QWeb
Suite Setup       SuiteStart
Suite Teardown    SuiteEnd
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome
${value}      ${EMPTY}

*** Test Cases ***
Upload files with index
    SetConfig           DefaultTimeout          1s
    UploadFile          1                       test1.txt
    ExecuteJavaScript   return document.querySelector('#myFile1').value   $value
    ShouldBeEqual       ${value}                C:\fakepath\test1.txt
    UploadFile          2                       test2.txt
    ExecuteJavaScript   return document.querySelector('#myFile2').value   $value
    ShouldBeEqual       ${value}                C:\fakepath\test2.txt

Upload files with locator
    UploadFile          Uploadme                       test1.txt
    ExecuteJavaScript   return document.querySelector('#myFile1').value   $value
    ShouldBeEqual       ${value}                       C:\fakepath\test1.txt

Upload with xpath
    UploadFile          //*[@id\='myFile3']    test2.txt
    ExecuteJavaScript   return document.querySelector('#myFile3').value   $value
    ShouldBeEqual       ${value}                       C:\fakepath\test2.txt

Upload with Index, visible only
    GoTo                ${BASE_URI}/upload_shadow_frame_visibility.html
    UploadFile          1                       test1.txt
    UploadFile          2                       test2.txt
    VerifyElementText   result-light-first      Selected: test1.txt       tag=div
    VerifyElementText   r1                      Selected: test2.txt       tag=div   

    # should fail, only 2 visible in light-dom
    Run Keyword And Expect Error    QWebElementNotFoundError*   UploadFile          3                       test2.txt   timeout=1


Upload with Index, visibility off
    GoTo                ${BASE_URI}/upload_shadow_frame_visibility.html
    UploadFile          1                       test1.txt   visibility=False
    UploadFile          2                       test2.txt   visibility=False
    UploadFile          3                       test1.txt   visibility=False
    VerifyElementText   result-light-first      Selected: test1.txt       tag=div
    VerifyElementText   result-light-last       Selected: test2.txt       tag=div
    VerifyElementText   r1                      Selected: test1.txt       tag=div   

    # should fail, only 4 in light-dom
    Run Keyword And Expect Error    QWebElementNotFoundError*   UploadFile          5     test2.txt   visibility=False    timeout=1


Upload with Index, visible only, shadow dom included
    [Setup]             SetConfig     ShadowDom   On
    [Teardown]          ResetConfig   ShadowDom 
    GoTo                ${BASE_URI}/upload_shadow_frame_visibility.html
    UploadFile          1                       test1.txt
    UploadFile          2                       test2.txt
    UploadFile          3                       test1.txt
    VerifyElementText   result-light-first      Selected: test1.txt       tag=div
    VerifyElementText   result-shadow           Selected: test2.txt       tag=div
    VerifyElementText   r1                      Selected: test1.txt       tag=div     

    # should fail, only 3 visible in both doms
    Run Keyword And Expect Error    QWebElementNotFoundError*   UploadFile          4     test2.txt   timeout=1

Upload with Index, include non-visible, shadow dom included
    [Setup]             SetConfig     ShadowDom   On
    [Teardown]          ResetConfig   ShadowDom 
    GoTo                ${BASE_URI}/upload_shadow_frame_visibility.html
    UploadFile          3                       test1.txt       visibility=False
    UploadFile          4                       test2.txt       visibility=False
    UploadFile          6                       test1.txt       visibility=False
    UploadFile          8                       test2.txt       visibility=False
    VerifyElementText   result-nested           Selected: test1.txt       tag=div
    VerifyElementText   result-light-last       Selected: test2.txt       tag=div
    VerifyElementText   r2                      Selected: test1.txt       tag=div   
    VerifyElementText   r4                      Selected: test2.txt       tag=div       

    # should fail, only 8 in both doms and all frames
    Run Keyword And Expect Error    QWebElementNotFoundError*   UploadFile          9     test2.txt    visibility=False   timeout=1

*** Keywords ***
SuiteStart
     OpenBrowser    ${BASE_URI}/upload.html    ${BROWSER}  --headless

SuiteEnd
    ResetConfig    DefaultTimeout
    CloseAllBrowsers