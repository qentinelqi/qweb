*** Settings ***
Documentation    Tests for table keywords
Library          QWeb
Library          Collections
Suite Setup      OpenBrowser    file://${CURDIR}/../resources/table3.html  ${BROWSER}  --headless      
Suite Teardown   CloseBrowser
Test Timeout     60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Row count
    UseTable                Firstname
    ${amount}               GetTableRow             //last
    Should Be Equal         '${amount}'             '5'
    # exluding headers:
    ${content}              GetTableRow             //last      skip_header=True
    Should Be Equal         '${content}'            '4'

Get specific Column header
    UseTable                Firstname
    ${value}=               GetColumn              4
    Should Be Equal         ${value}               Email

Get All columns to list
    UseTable                Firstname
    ${all}=                 GetColumn
    ${length}=              Get Length       ${all}
    Should Be Equal As Integers    ${length}    6
    List Should Contain Value      ${all}       City
    Log List   ${all}

VerifyColumn value with thead table
    UseTable                Firstname
    # Column must exist in specific index
    VerifyColumn            Email    4
    # Column exists at any position
    VerifyColumn            City
    # Column exists, 0 given as index
    VerifyColumn            Country   0         
    

Column count thead table
    UseTable                Firstname
    ${amount}               GetColumnCount
    Should Be Equal As Integers         ${amount}             6
    