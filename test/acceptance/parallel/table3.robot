*** Settings ***
Documentation    Tests for table keywords
Library          QWeb
Library          Collections
Suite Setup      OpenBrowser    ${BASE_URI}/table3.html  ${BROWSER}  --headless      
Suite Teardown   CloseBrowser
#Test Timeout     60 seconds

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
    ${value}=               GetColHeader              4
    Should Be Equal         ${value}               Email

Get All columns to list
    UseTable                Firstname
    ${all}=                 GetColHeader
    ${length}=              Get Length       ${all}
    Should Be Equal As Integers    ${length}    6
    List Should Contain Value      ${all}       City
    Log List   ${all}

VerifyColumn value with thead table
    UseTable                Firstname
    # Column must exist in specific index
    VerifyColHeader            Email    4
    # Column exists at any position
    VerifyColHeader            City
    # Column exists, 0 given as index
    VerifyColHeader            Country   0         
    

Column count thead table
    UseTable                Firstname
    ${amount}               GetColHeaderCount
    Should Be Equal As Integers         ${amount}             6


VerifyTable Duplicated columns
    UseTable                Table with Duplicate Columns
    # exact row/column coordinates, partial_match False
    VerifyTable             r2/c5    john.doe2@example.com    partial_match=False
    Run Keyword And Expect Error     QWebValueError*                 
    ...                        VerifyTable                    r2/c5    john                     partial_match=False    timeout=3

    # with column text in coordinates, partial_match=False
    VerifyTable             r2/c?Email    john.doe2@example.com        partial_match=False
    
    # with column text in coordinates, partial_match True
    # should match the first column containing "Email"
    VerifyTable             r2/c?Email    john.doe@    partial_match=True


Click Cells Duplicated columns
    UseTable                Table with Duplicate Columns
    # exact row/column coordinates
    ClickCell               r2/c5    tag=a
    VerifyAlertText         Row 1: Secondary Email address copied!
    CloseAlert              Accept
    
    # with column text in coordinates, partial_match=False
    ClickCell               r2/c?Email    partial_match=False    tag=a
    VerifyAlertText         Row 1: Secondary Email address copied!
    CloseAlert              Accept
    
    # with column text in coordinates, partial_match=True
    ClickCell               r2/c?Email    partial_match=True     tag=a
    VerifyAlertText         Row 1: Primary Email address copied!
    CloseAlert              Accept