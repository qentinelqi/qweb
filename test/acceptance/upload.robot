*** Settings ***
Documentation     Tests for UploadFile keyword
Library           QWeb
Suite Setup       SuiteStart
Suite Teardown    CloseBrowser
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

*** Keywords ***
SuiteStart
     OpenBrowser    file://${CURDIR}/../resources/upload.html    ${BROWSER}  --headless
