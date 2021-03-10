*** Settings ***
Library             QWeb

*** Variables ***

*** Keywords ***
Setup Tests
    Open Browser    about:blank    gc
    Set Window Size   1600    900


Appstate Google
    Go To           http://www.google.fi/
