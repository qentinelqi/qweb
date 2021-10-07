*** Settings ***
Resource            ../resources/keywords.robot
Suite Setup         Setup Browser
Suite Teardown      Close All Browsers
Test Timeout        1min

*** Test Cases ***
#Tuotteet
#    [Tags]          Matematiikka
#    Appstate        Sanoma
#    ClickHeader     Tuotteet
#
#    Typetext        Hae sarjan tai tuotteen nimellä    matematiikka
#
#    Sleep           2                                   # temp fix until verifytext change has been merged
#    VerifyText      YO Pitkä matematiikka

Opettajat
    [Tags]          Opettajat
    Appstate        Sanoma
    ClickHeader     Opettajat
    VerifyText      Kiinnostavat artikkelit, opetusalan uudet tuulet sekä tietenkin opevinkit.

Opiskelijat
    [Tags]          Opiskelijat
    Appstate        Sanoma
    ClickHeader     Opiskelijat
    ClickText       Siirry ostoksille
    ClickText       Kemia

Vanhemmat
    [Tags]          Vanhemmat
    Appstate        Sanoma
    ClickHeader     Vanhemmat
    ClickText       Ohjelmointi
