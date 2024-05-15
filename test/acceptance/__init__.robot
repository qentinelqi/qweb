*** Settings ***
Suite Setup    Check Http Server

*** Variables ***
${ON_HTTP_SERVER}=    ${FALSE}

*** Keywords ***
Check Http Server
    IF    $ON_HTTP_SERVER
        ${BASE_URI}=    Set Variable    http://127.0.0.1:8000
    ELSE
        ${BASE_URI}=    Set Variable    file:///${CURDIR}/../resources
    END
    Set Global Variable    ${BASE_URI}
