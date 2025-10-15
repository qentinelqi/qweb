*** Settings ***
Documentation       Tests for icon keywords
Library             QWeb
Library             String
Suite Setup         OpenBrowser    about:blank    ${BROWSER}
Test Setup          GoTo    ${BASE_URI}/spinner_test.html
Test Teardown       ResetConfig    SpinnerCSS
Suite Teardown      CloseBrowser
#Test Timeout        60 seconds

*** Variables ***
${BROWSER}                  chrome

*** Test Cases ***
Spinners not visible
    VerifyText              Spinner Test Page
    SetConfig               SpinnerCSS     lightning-spinner, .spinner
    ${conf_locators}=       GetConfig      SpinnerCSS
    ${locators_list}=       Create List    ${conf_locators}
    ${spinner_busy}=        Evaluate       QWeb.internal.xhr.is_spinner_busy(${locators_list})
    Should Not Be True      ${spinner_busy}

Normal Spinner visible
    VerifyText              Spinner Test Page
    # Set custom spinner locators just to makes sure that SetConfig works
    SetConfig               SpinnerCSS     .spinner
    ${conf_locators}=       GetConfig      SpinnerCSS
    ${locators_list}=       Create List    ${conf_locators}
    ${spinner_busy}=        Evaluate       QWeb.internal.xhr.is_spinner_busy(${locators_list})
    Should Not Be True      ${spinner_busy}
    ClickText               Toggle Normal Spinner
    

    ${spinner_busy}=        Evaluate       QWeb.internal.xhr.is_spinner_busy(${locators_list})
    Should Be True         ${spinner_busy}
    # hide to avoid unnecessary waiting
    SetConfig               SpinnerCSS     none
    ClickText               Hide Normal Spinner
    SetConfig               SpinnerCSS     lightning-spinner, .spinner
    ${locators_list}=       Create List    ${conf_locators}
    ${spinner_busy}=        Evaluate       QWeb.internal.xhr.is_spinner_busy(@{locators_list})
    Should Not Be True      ${spinner_busy}

SF Style Spinner behind dialog, but not hidden
    VerifyText              Spinner Test Page
    # Set custom spinner locators just to makes sure that SetConfig works
    SetConfig               SpinnerCSS     lightning-spinner, .spinner
    ${conf_locators}=       GetConfig      SpinnerCSS
    ${locators_list}=       Create List    ${conf_locators}
    ${spinner_busy}=        Evaluate       QWeb.internal.xhr.is_spinner_busy(${locators_list})
    Should Not Be True      ${spinner_busy}
    # Click button to show spinner behind dialog/element
    # Special case due to some lazy handling of spinners;
    # In some cases spinner is not hidden etc. when behind element
    ClickText               SF Style Spinner 
    ${spinner_busy}=        Evaluate       QWeb.internal.xhr.is_spinner_busy(${locators_list})
    Should Not Be True      ${spinner_busy}

SF Style Spinner fully visible
    VerifyText              Spinner Test Page
    # Click button to show spinner behind dialog/element and again to make it fully visible
    ClickText               SF Style Spinner 
    ClickText               Bring SF Style Spinner to Front
    # Set custom spinner locators just to makes sure that SetConfig works
    SetConfig               SpinnerCSS     lightning-spinner, .spinner
    ${conf_locators}=       GetConfig      SpinnerCSS
    ${locators_list}=       Create List    ${conf_locators}
    ${spinner_busy}=        Evaluate       QWeb.internal.xhr.is_spinner_busy(${locators_list})
    Should Be True          ${spinner_busy}

