*** Settings ***
Documentation             Tests for QWeb command line interface
Library                   QWeb
Library                   Process
Suite Setup               Get Python executable
Test Timeout              60 seconds

*** Variables ***


*** Test Cases ***
Get version
    [Documentation]       Verify that typing python QWeb -V and python QWeb --version displays version info
    ${result}=            Run Process                ${python_ver}               -m    QWeb    -V           shell=True    stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           QWeb
    ${result}=            Run Process                ${python_ver}               -m    QWeb    --version    shell=True    stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           QWeb
    LogToConsole          ${result.stdout}


Print help
    [Documentation]       Verify that typing python QWeb -h and python QWeb --help displays help
    ${result}=            Run Process                ${python_ver}               -m    QWeb    -h           shell=True    stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           lists keywords based on input string
    ${result}=            Run Process                ${python_ver}               -m    QWeb    --help       shell=True    stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           lists keywords based on input string
    # without any switches help should also be displayed
    ${result}=            Run Process                ${python_ver}               -m    QWeb    --help       shell=True    stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           lists keywords based on input string


List All
    [Documentation]       Verify that typing python QWeb -A and python QWeb --all lists all keywords
    ${result}=            Run Process                ${python_ver}               -m    QWeb    -A           shell=True    stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           Verify Table
    ${result}=            Run Process                ${python_ver}               -m    QWeb    --all        shell=True    stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           Verify Table


List with Input
    [Documentation]       Verify that typing python QWeb -A and python QWeb --all lists all keywords
    ${result}=            Run Process                ${python_ver}               -m    QWeb    -L           Get           shell=True                  stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           Get List
    Should Contain        ${result.stdout}           Get Text
    Should Not Contain    ${result.stdout}           Verify
    ${result}=            Run Process                ${python_ver}               -m    QWeb    --list       Get           shell=True                  stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           Get List
    Should Contain        ${result.stdout}           Get Text
    Should Not Contain    ${result.stdout}           Verify


Show doc for a keyword
    [Documentation]       Verify that typing python QWeb -S and python QWeb --show displays keyword documentation
    ${result}=            Run Process                ${python_ver}               -m    QWeb    -S           TypeText      shell=True                  stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           Type given text to a text field.
    ${result}=            Run Process                ${python_ver}               -m    QWeb    --show       Type Text     shell=True                  stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           Type given text to a text field.
    ${result}=            Run Process                ${python_ver}               -m    QWeb    --show       type text     shell=True                  stdout=${TEMPDIR}/stdout.txt
    Should Contain        ${result.stdout}           Type given text to a text field.


*** Keywords ***
Get Python executable
    ${sys}=               Evaluate                   sys.modules["sys"]
    Set Suite Variable    ${python_ver}              ${sys.executable}
    Log                   ${python_ver}
