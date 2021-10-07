*** Settings ***
Documentation       Tests for download keywords
Library             Process
Library             OperatingSystem
Library             QWeb
Suite Setup         Download Suite Setup
Suite Teardown      Download Suite Teardown
Test Teardown       Remove Small and Large Files
Test Timeout        1min
Force Tags          FLASK

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Verify File Download Slow Bandwidth
    [Tags]    PROBLEM_IN_SAFARI		PROBLEM_IN_FIREFOX
    VerifyText       Download large csv file
    ExpectFileDownload
    ClickText        Download large csv file
    ${downloaded}=   VerifyFileDownload    20s
    Should Contain   ${downloaded}         large.csv
    FileShouldExist  ${downloaded}

Verify File Download Fails If Multiple Files Found
    [Tags]    PROBLEM_IN_SAFARI
    VerifyText      Download small csv file
    ExpectFileDownload
    Two Files Are Downloaded Without ExpectFileDownload Keyword
    Run Keyword And Expect Error    ValueError: Found more than one file that was modified
    ...   VerifyFileDownload    2s


Verify File Download Fail No File Downloading
    [Tags]    PROBLEM_IN_SAFARI
    VerifyText      Download small csv file
    ExpectFileDownload
    Run Keyword And Expect Error    ValueError: Could not find any modified files after 3.0s
    ...    VerifyFileDownload    3s


Verify File Download Fail Timeout
    [Tags]    PROBLEM_IN_SAFARI		PROBLEM_IN_FIREFOX
    VerifyText      Download small csv file
    ExpectFileDownload
    ClickText       Download large csv file
    Run Keyword And Expect Error    ValueError: Could not find any modified files after 3.0s
    ...    VerifyFileDownload    3s

*** Keywords ***
Two Files Are Downloaded Without ExpectFileDownload Keyword
    ClickText       Download small csv file
    VerifyFileDownload
    ClickText       Download small csv file
    Sleep    2

Download Suite Setup
    OpenBrowser    about:blank    ${BROWSER}
    Set Environment Variable    FLASK_APP    download_app.py
    ${path_to_app}=   Evaluate    os.path.realpath(r"${CURDIR}${/}..${/}resources${/}download")    modules=os
    ${flask_handle}=    Start Process   flask run    shell=True   cwd=${path_to_app}
    Sleep           5    # Required for the server to start
    Process Should Be Running    ${flask_handle}    Flask server was not running
    GoTo            http://127.0.0.1:5000/
    ${found}    Run Keyword And Return Status    VerifyText       Download small csv file
    Run Keyword Unless    '${found}' == 'PASS'   run keywords
    ...    GoTo     http://127.0.0.1:5000/
    ...    AND      VerifyText       Download small csv file

Download Suite Teardown
    CloseAllBrowsers
    Terminate All Processes
    Remove Directory    ~/TmpDownloads    ${true}

Remove Small and Large Files
    Remove File   ~/Downloads/small.csv
    Remove File   ~/Downloads/large.csv
    Remove File   ~/Downloads/large (1).csv
    Remove File   ~/Downloads/small (1).csv
    Run Keyword And Ignore Error    Remove Crdownload

Remove Crdownload
    Sleep    2s
    Remove File   ~/Downloads/large.csv.crdownload
