
*** Settings ***
Library             String
Library             QWeb
Library             ../libraries/SanomaWeb.py

*** Variables ***
${ostoskori}        //*[@class='action showcart']
${Hae}              //*[@title='Hae']
${Poista}           //*[@title='Remove item']
${ENTER}            \ue007

*** Keywords ***
Setup Browser
    Open Browser    about:blank    gc
    Set Window Size   1400    900


#############################
# APPSTATES                 #
#############################
Appstate
    [Documentation] 	Checks which actions should be taken prior to testing and does them
    [Arguments]         ${state}
    ${state}=           Convert To Lowercase    ${state}
    Run Keyword If     '${state}' == 'sanoma'
    ...                 Sanoma


Sanoma
    Go To               http://www.sanomapro.fi/
    ${cookie}=          IsText      Hyväksyn
    Run Keyword If      ${cookie}
    ...                 ClickText   Hyväksyn
