*** Settings ***
Library             Dialogs
Library             QWeb
Library             String


*** Variables ***
${BROWSER}                  chrome


*** Keywords ***
Setup Browser
    Open Browser    about:blank        ${BROWSER}
    SetConfig       CSSSelectors       True
    SetConfig       LineBreak          None
    SetConfig       checkinputvalue    True

End suite
    Close All Browsers
    Sleep    2

Appstate
    [Documentation]     AppState handler
    [Arguments]         ${state}
    ${state}=           Convert To Lowercase    ${state}
    
    Run Keyword If     '${state}' == 'qentinel'
    ...                 Qentinel
    
    Run Keyword If     '${state}' == 'yliopisto'
    ...                 Yliopisto
    
Qentinel 
    Go To           https://qentinel.com/en



