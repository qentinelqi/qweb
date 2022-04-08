*** Settings ***
Documentation       Tests for icon keywords
Library             QWeb
Suite Setup         OpenBrowser    about:blank    ${BROWSER}
Test Setup          GoTo    file://${CURDIR}/../resources/items.html
Suite Teardown      CloseBrowser
Library             Dialogs
Test Timeout        1min

*** Variables ***
${BROWSER}                  chrome
${BASE_IMAGE_PATH}          ${CURDIR}${/}..${/}resources${/}pics_and_icons${/}icons

*** Test Cases ***
Click icons
    [Tags]                  ICON
    ${is_retina}=           GetConfig    RetinaDisplay
    Log                     Retina display detected: ${is_retina}
    VerifyIcon              person                template_res_w=1920
    ClickIcon               person                template_res_w=1920
    VerifyText              person is my tooltip value!
    VerifyIcon              lock                  template_res_w=1920
    ClickIcon               lock                  template_res_w=1920
    VerifyText              Lock is my title value!
    ClickIcon               screen                 template_res_w=1920
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


Click icons new screenshot
    [Tags]                  ICON
    ClickIcon               person                template_res_w=1920
    ClickIcon               power                 template_res_w=1920
    ClickText               Hide                  template_res_w=1920
    Run Keyword And Expect Error    QWebElementNotFoundError:*   ClickIcon      person   timeout=3


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
    [Tags]                  jailed	PROBLEM_IN_FIREFOX      RESOLUTION_DEPENDENCY
    CloseAllBrowsers
    OpenBrowser             file://${CURDIR}/../resources/input.html    chrome
    ClickIcon               leftright
    WriteText               FooBar
    VerifyInputValue        odjdq               Foobar     selector=id


*** Keywords ***
RemoveFiles
    [Documentation]     Remove files used in CaptureIcon test
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_1.png
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_2.png
    RemoveFile          ${BASE_IMAGE_PATH}/capture_icon_3.png    
