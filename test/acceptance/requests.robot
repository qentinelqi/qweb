*** Settings ***
Documentation     Tests for cookies keywords
Library           Collections
Library           Process
Library           OperatingSystem
Library           QWeb
Suite Setup       OpenBrowser    about:blank    ${BROWSER}
Test Setup        Start Flask Server
Test Teardown     Terminate All Processes
Suite Teardown    CloseAllBrowsers
Test Timeout      1min
Force Tags        FLASK

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Save file using icon as a locator
    GoTo            http://127.0.0.1:5000/
    VerifyItem      screen
    Run keyword and expect error    QWebFileNotFoundError:*
    ...             UsePdf      unnamediddqd11222333544485923.pdf
    SaveFile        screen      anchor=2
    UsePdf          unnamed.pdf
    VerifyPdfText   Simple PDF File
    RemovePdf

Save file using text as a locator and rename to testpdf
    Run keyword and expect error    QWebFileNotFoundError:*
    ...             UsePdf   testpdf.pdf
    SaveFile        Click here to download PDF  testpdf.pdf
    UsePdf          testpdf.pdf
    VerifyPdfText   Simple PDF File
    RemovePdf


*** Keywords ***
Start Flask Server
    Set Environment Variable    FLASK_APP    requests_app.py
    ${path_to_app}=   Evaluate    os.path.realpath(r"${CURDIR}${/}..${/}resources${/}requests")  modules=os
    ${flask_handle}=    Start Process   flask run    shell=True   cwd=${path_to_app}
    Sleep           5    # Required for the server to start
    Process Should Be Running    ${flask_handle}    Flask server was not running
