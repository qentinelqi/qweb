*** Settings ***
Documentation       Tests for icon keywords
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}
Test Setup          GoTo    http://127.0.0.1:8000/items.html
Suite Teardown      CloseBrowser
Library             Dialogs
Test Timeout        60 seconds

*** Variables ***
${BROWSER}                  chrome
${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}..${/}resources${/}pics_and_icons${/}icons

*** Test Cases ***
Click icons
    [Tags]                  ICON    PROBLEM_IN_MACOS    RESOLUTION_DEPENDENCY
    Set Config              WindowSize   1920x1080
    ClickIcon               person                template_res_w=1920
    VerifyText              person is my tooltip value!
    ClickIcon               lock                  template_res_w=1920
    VerifyText              Lock is my title value!
    ClickIcon               screen                template_res_w=1920
    VerifyText              screen is my data-icon value!

Verify icons
    [Tags]                  ICON
    SetConfig               LogMatchedIcons       True
    VerifyIcon              person                template_res_w=1920
    VerifyIcon              power                 template_res_w=1920
    VerifyIcon              paperclip             template_res_w=1920
    VerifyIcon              infinity              template_res_w=1920
    VerifyIcon              Lock                  template_res_w=1920
    VerifyIcon              screen                template_res_w=1920
    SetConfig               LogMatchedIcons       False

Verify matching color
    [Tags]                  ICON
    SetConfig               LogMatchedIcons       True
    # colored image with default grayscale setting, should be found 
    VerifyIcon              infinity_red          template_res_w=1920
    # colored image compared with colors, should not be found 
    Run Keyword And Expect Error   QWebElementNotFoundError*
    ...                            VerifyIcon    infinity_red          
    ...                                          template_res_w=1920    
    ...                                          tolerance=0.99    
    ...                                          grayscale=False
    ...                                          timeout=3

    SetConfig               LogMatchedIcons       False

IsIcon matching color
    [Tags]                  ICON
    SetConfig               LogMatchedIcons       True
    # colored image with default grayscale setting, should be found 
    ${result}               isIcon                  infinity_red
    Should Be True          ${result}
    # colored image compared with colors, should not be found 
    ${result_color}         isIcon                  infinity_red
    ...                                             tolerance=0.99
    ...                                             grayscale=False
    Should Not Be True      ${result_color}
    
    SetConfig               LogMatchedIcons       False

Click icons new screenshot
    [Tags]                  ICON    PROBLEM_IN_MACOS    RESOLUTION_DEPENDENCY
    Set Config              WindowSize   1920x1080
    ClickIcon               person                template_res_w=1920
    ClickIcon               power                 template_res_w=1920
    ClickText               Hide                  template_res_w=1920
    Run Keyword And Expect Error    QWebElementNotFoundError:*   ClickIcon      person   timeout=3

Click icon color
    [Tags]                  ICON    PROBLEM_IN_MACOS
    Set Config              WindowSize   1920x1080
    # colored image compared with colors, should not be found 
    Run Keyword And Expect Error   QWebElementNotFoundError*
    ...                            ClickIcon    infinity_red          
    ...                                          template_res_w=1920    
    ...                                          tolerance=0.99    
    ...                                          grayscale=False
    ...                                          timeout=3
    # colored image with default grayscale setting, should be found 
    ClickIcon              infinity_red          template_res_w=1920
    VerifyText             Infinity is my alt value!
    ClickText              Show Red Infinity
    ClickIcon              infinity_red          grayscale=False
    VerifyText             Infinity_red is my alt value!

Capture icons and verify them
    [Tags]                  ICON
    [Teardown]              RemoveFiles
    SetConfig               SearchMode          None
    
    CaptureIcon             person     ${BASE_IMAGE_PATH}     capture_icon_1.png
    VerifyIcon              capture_icon_1
    CaptureIcon             power      ${BASE_IMAGE_PATH}     capture_icon_2.png
    VerifyIcon              capture_icon_2
    CaptureIcon             /html/body/table/tbody/tr[1]/td[6]/img      ${BASE_IMAGE_PATH}
    ...                     capture_icon_3.png
    VerifyIcon              capture_icon_3

IsIcon True
    [Tags]                  ICON
    ${result}               isIcon                  paperclip                   template_res_w=1920
    Should Be True          ${result}

IsIcon False
    [Tags]                  ICON
    ${result}               isIcon                  plane
    Should Not Be True      ${result}

WriteText
    [Tags]                  jailed	PROBLEM_IN_FIREFOX      RESOLUTION_DEPENDENCY    PROBLEM_IN_MACOS
    CloseAllBrowsers
    OpenBrowser             http://127.0.0.1:8000/input.html    chrome
    ClickIcon               leftright
    WriteText               FooBar
    VerifyInputValue        odjdq               Foobar     selector=id


*** Keywords ***
RemoveFiles
    [Documentation]     Remove files used in CaptureIcon test
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_1.png
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_2.png
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_3.png