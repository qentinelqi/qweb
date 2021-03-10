*** Settings ***
Library             Dialogs
Library             QWeb
Library             ../libraries/SteamWeb.py

*** Keywords ***
Setup Browser
    Open Browser        about:blank    gc
    Set Window Size     1920    1080

Appstate Steam
    Go To               http://www.steampowered.com/

