*** Settings ***
Documentation     Tests for Mouse keywords and coordinates
Library           QWeb
Suite Setup       OpenBrowser    ${BASE_URI}/mouse.html    ${BROWSER}
Suite Teardown    CloseBrowser
Test Timeout      60 seconds

*** Variables ***
${BROWSER}    chrome

*** Test Cases ***
Toast notifications in the normal browser
    [tags]              toast    notify
    ToastNotify         Success step!                   success        center         timeout=10
     # Should not be found, toasts are in shadow dom
    VerifyNoText        Success step                    timeout=2      delay=1

    ToastNotify         Heads up! Check this part.      warning        top-right      timeout=4 
    ToastNotify         Something went wrong!           error          bottom-left    timeout=4 
    # The next one should be found with Shadow dom search set on
    SetConfig           ShadowDOM                       On
    # Custom font size and heading
    ToastNotify         Informational message           info           bottom-right   font_size=32  heading=QWeb Notification   timeout=10
    VerifyText          Informational message 
    LogScreenshot
    SetConfig           ShadowDOM                       Off


Toast notifications in the headless browser
    [tags]              toast    notify
    [Setup]             CloseAllBrowsers
    OpenBrowser    ${BASE_URI}/mouse.html    ${BROWSER}    --headless 

    ToastNotify         Success step!                   success        center         timeout=10
     # Should not be found, toasts are in shadow dom
    VerifyNoText        Success step                    timeout=2      delay=1

    ToastNotify         Heads up! Check this part.      warning        top-right      timeout=4 
    ToastNotify         Something went wrong!           error          bottom-left    timeout=4 
    # The next one should be found with Shadow dom search set on
    SetConfig           ShadowDOM                       On
    # Custom font size and heading
    ToastNotify         Informational message           info           bottom-right   font_size=32  heading=QWeb Notification   timeout=10
    VerifyText          Informational message 
    LogScreenshot
    SetConfig           ShadowDOM                       Off


