*** Settings ***
Documentation       Qentinel QWeb demo
Resource            ${CURDIR}${/}../resources/keywords.robot
Suite Setup         Setup Browser
Suite Teardown      End suite
Test Timeout        2min


*** Test Cases ***

Contact Us
    [Documentation]    Registration to Qentinel contact form
    [tags]      ok
    Appstate    Qentinel
    ClickText   Contact us
    VerifyText  Contact request
    TypeText    First name            Jane
    TypeText    Last name             Doe
    TypeText    Email*                jane.doe@gmail.com
    TypeText    Phone                 040 123 4567
    TypeText    Company name          Qentinel
    TypeText    Message               I need help in test automation
    ClickText   Send
    VerifyText  Select all

Test Menu
    [Documentation]    Checking Qentinel success stories
    [tags]      nok
    Appstate    Qentinel
    ClickText   Qentinel Pace
    ClickText   Overview
    VerifyText  With Qentinel Pace, you can utilize the full potential of robotic software testing, which is the future of test automation.
    ClickText   Success stories
    ScrollText  Next
    ClickText   Next
    ScrollText  KONE
    ClickText   KONE
    VerifyText  Around one billion people use KONE solutions every day
