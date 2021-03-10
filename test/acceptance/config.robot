*** Settings ***
Documentation     Tests for Config keywords
Library           QWeb
Test Timeout      1min

*** Variables ***
${BROWSER}    chrome
${URL}        file://${CURDIR}/../resources/checkbox.html

*** Test Cases ***
Test ScreenshotType Config
    ${VAL}=      GetConfig     ScreenshotType
    ShouldBeEqual    ${VAL}    screenshot
    SetConfig    ScreenshotType    all
    ${VAL}=      GetConfig     ScreenshotType
    ShouldBeEqual    ${VAL}    all
    # Reset all
    ResetConfig
    ${VAL}=      GetConfig     ScreenshotType
    ShouldBeEqual    ${VAL}    screenshot

Test CssSelectors Config
    ${VAL}=      GetConfig     CssSelectors
    ShouldBeEqual    ${VAL}    ${True}
    SetConfig    CssSelectors  off
    ${VAL}=      GetConfig     CssSelectors
    ShouldBeEqual    ${VAL}    ${False}
    # Reset single parameter
    ResetConfig  CssSelectors
    ${VAL}=      GetConfig     CssSelectors
    ShouldBeEqual    ${VAL}    ${True}

Test inViewport Config
    ${VAL}=      GetConfig     inViewport
    ShouldBeEqual    ${VAL}    ${False}
    SetConfig    inViewport    on
    ${VAL}=      GetConfig     inViewport
    ShouldBeEqual    ${VAL}    ${True}
    # Reset single parameter
    ResetConfig  inViewport
    ${VAL}=      GetConfig     inViewport
    ShouldBeEqual    ${VAL}    ${False}

Test OffsetCheck Config
    ${VAL}=      GetConfig     OffsetCheck
    ShouldBeEqual    ${VAL}    ${True}
    SetConfig    OffsetCheck   off
    ${VAL}=      GetConfig     OffsetCheck
    ShouldBeEqual    ${VAL}    ${False}
    # Reset single parameter
    ResetConfig  OffsetCheck
    ${VAL}=      GetConfig     OffsetCheck
    ShouldBeEqual    ${VAL}    ${True}

Test Visibility Config
    OpenBrowser  ${URL}        ${BROWSER}   --headless
    ${VAL}=      GetConfig     Visibility
    ShouldBeEqual    ${VAL}    ${True}
    VerifyNoText     Hiddenbox
    SetConfig    Visibility    False
    ${VAL}=      GetConfig     Visibility
    ShouldBeEqual    ${VAL}    ${False}
    VerifyText      Hiddenbox
    CloseAllBrowsers
    # Reset single parameter
    ResetConfig  Visibility
    ${VAL}=      GetConfig     Visibility
    ShouldBeEqual    ${VAL}    ${True}

Test PartialMatch Config
    ${VAL}=      GetConfig     PartialMatch
    ShouldBeEqual    ${VAL}    ${True}
    SetConfig    PartialMatch  False
    ${VAL}=      GetConfig     PartialMatch
    ShouldBeEqual    ${VAL}    ${False}
    # Reset single parameter
    ResetConfig  PartialMatch
    ${VAL}=      GetConfig     PartialMatch
    ShouldBeEqual    ${VAL}    ${True}

Test ClearKey Config
    ${VAL}=      GetConfig     ClearKey
    ShouldBeEqual    ${VAL}    ${None}
    SetConfig    ClearKey      {CONTROL + A}
    ${VAL}=      GetConfig     ClearKey
    ShouldBeEqual    ${VAL}    {CONTROL + A}
    #Reset single parameter
    ResetConfig  ClearKey
    ${VAL}=      GetConfig     ClearKey
    ShouldBeEqual    ${VAL}    ${None}

Test WindowFind Config
    ${VAL}=      GetConfig      WindowFind
    ShouldBeEqual    ${VAL}    ${False}
    SetConfig    WindowFind    True
    ${VAL}=      GetConfig     WindowFind
    ShouldBeEqual    ${VAL}    ${True}
    # Reset single parameter
    ResetConfig  WindowFind
    ${VAL}=      GetConfig     WindowFind
    ShouldBeEqual    ${VAL}    ${False}

Test Log all configs
    ${config}=    GetConfig
    Log           ${config}     console=True
