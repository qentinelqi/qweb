*** Settings ***
Documentation       Test for screenshot functionality
Library             QWeb
Library             OperatingSystem
Suite Setup         OpenBrowser    file://${CURDIR}/../resources/text.html    ${BROWSER}  --headless
Suite Teardown      CloseBrowser
Test Timeout        1min

*** Variables ***
${SCREENSHOT_NAME}    test_screen_shot.png
${BROWSER}    chrome

*** Keywords ***
Remove Test Screenshot
    [Arguments]     ${file_name}
    Remove File     ${OUTPUT_DIR}${/}screenshots${/}${file_name}

*** Test Cases ***
Screenshot Functionality Works
    File Should Not Exist    ${OUTPUT_DIR}${/}screenshots${/}${SCREENSHOT_NAME}
    LogScreenshot    ${SCREENSHOT_NAME}
    File Should Exist    ${OUTPUT_DIR}${/}screenshots${/}${SCREENSHOT_NAME}    Screenshot was not taken
    [Teardown]    Remove Test Screenshot    ${SCREENSHOT_NAME}

Screenshot Is Taken On Exception
    ${amount_of_screenshots_before}=   count files in directory    ${OUTPUT_DIR}${/}screenshots
    ...    pattern=screenshot*.png

    ${error}=    Run Keyword and Expect Error    *    VerifyText    not found on test page  3
    should contain    ${error}    QWebElementNotFoundError
    ${amount_of_screenshots_after}=   count files in directory    ${OUTPUT_DIR}${/}screenshots
    ...    pattern=screenshot*.png

    ${result}=    evaluate   (${amount_of_screenshots_before} + 1) == ${amount_of_screenshots_after}
    Should Be True    ${result}    Screenshot amount did not grow by one

Test VerifyApp
    VerifyApp      verifyapp
    Directory Should exist         ${OUTPUT_DIR}/verifyapp
    File Should Exist              ${OUTPUT_DIR}/verifyapp/Test_VerifyApp_verifyapp_ref.png
    VerifyApp                      verifyapp
    Go To                          file://${CURDIR}/../resources/dropdown.html
    Run keyword and expect error   Images differ    VerifyApp      verifyapp
    Remove File                    ${OUTPUT_DIR}/verifyapp/Test_VerifyApp_verifyapp_ref.png

Test VerifyApp Accuracy
    [Tags]         RESOLUTION_DEPENDENCY
    Go To          file://${CURDIR}/../resources/text.html
    SetConfig      VerifyAppAccuracy        0.0001
    VerifyApp      acctest
    Go To          file://${CURDIR}/../resources/dropdown.html
    VerifyApp      acctest
    SetConfig      VerifyAppAccuracy        0.9999
    Run keyword and expect error            Images differ    VerifyApp      acctest
