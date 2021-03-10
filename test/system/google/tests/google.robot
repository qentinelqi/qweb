*** Settings ***
Documentation       Goes to google and do searches
Resource            ../resources/keywords.robot
Suite Setup         Setup Tests
Suite Teardown      Close All Browsers
Test Timeout        1min

*** Test Cases ***
Do search
    [Documentation]         Test basic title search
    Appstate Google
    Set search strategy     matching input element  //*[@title="{}"]
    VerifyInputStatus       Haku                    Enabled
    Typetext                Haku                    Robotti
    ClickText               Google-haku

Do failing search
    [Documentation]         Test basic title search with wrong element
    Appstate Google
    Set search strategy     matching input element  //*[@nottitle="{}"]
    Run Keyword and Expect Error       ValueError: Webpage did not contain text "Haku"
    ...   Verify input status       Haku   Enabled
