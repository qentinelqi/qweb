*** Settings ***
Documentation       Goes to steam and checks if there are free games to play
Resource            ../resources/keywords.robot
Suite Setup         Setup Browser
Suite Teardown      Close All Browsers
Test Timeout        1min

*** Test Cases ***
View Free Games
    Appstate Steam
    SetConfig     PartialMatch  False
    SteamMenu     Browse    Free to Play
    SetConfig     PartialMatch  True
    VerifyText    Games
