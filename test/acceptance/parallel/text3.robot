*** Settings ***
Documentation                   Tests for text keywords
Library                         QWeb
Suite Setup                     OpenBrowser                 ${BASE_URI}/text.html                 ${BROWSER}                  --HEADLESS
Suite Teardown                  CloseBrowser
Test Timeout                    60 seconds

*** Variables ***
${BROWSER}                      chrome

*** Test Cases ***
VerifyAll String Without Source File With All Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_all
    VerifyAll                   consectetur

VerifyAll From File Content With All Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_all
    VerifyAll                   test5.txt

VerifyAll From File Content With All But One Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_all
    Run Keyword and Expect Error                            *                           VerifyAll                   test6.txt

VerifyAll From List All Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_all
    ${iddqd}=                   Create List                 between words 125 603,33    exercitation                qui officia
    ...                         Identifying text            :-)
    Verifyall                   ${iddqd}

VerifyAny String Without Source File With All Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    VerifyAny                   consectetur

VerifyAny Strings Without Source File With One Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    VerifyAny                   captain, consectetur

VerifyAny String Without Source File With None Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    Run Keyword and Expect Error                            QWebValueError: Could not find any of the texts*        VerifyAny                   captain

VerifyAny Strings Without Source File With None Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    Run Keyword and Expect Error                            QWebValueError: Could not find any of the texts*        VerifyAny                   captain, major

VerifyAny From File Content With All But One Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    VerifyAny                   test6.txt

VerifyAny From File Content With None Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    Run Keyword and Expect Error                            QWebValueError: Could not find any of the texts*        VerifyAny                   test7.txt

VerifyAny From List All Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    ${iddqd}=                   Create List                 between words 125 603,33    exercitation                qui officia
    ...                         Identifying text            :-)
    VerifyAny                   ${iddqd}

VerifyAny From List With All But One Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    ${iddqd}=                   Create List                 exercitation                qui officia                 This Should Not Be Found
    VerifyAny                   ${iddqd}

VerifyAny From List With None Found
    [tags]                      PROBLEM_IN_FIREFOX          verify_any
    ${iddqd}=                   Create List                 exercixxxtation             qxxui officiaxxx            This Should Not Be Found
    Run Keyword and Expect Error                            *                           VerifyAny                   ${iddqd}