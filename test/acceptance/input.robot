*** Settings ***
Documentation    Tests for input keywords
Library          QWeb
Library          OperatingSystem
Suite Setup      OpenBrowser    file://${CURDIR}/../resources/input.html    ${BROWSER}  --headless
Suite Teardown   CloseBrowser
Test Timeout     20 seconds

*** Variables ***
${BROWSER}    chrome
${Bar}        1
${foobar}     timeout

*** Test Cases ***

PressKey Paste
    [tags]                  jailed      paste
    CopyText                Test Automation rules
    PressKey                The Brave               {PASTE}
    VerifyInputValue        The Brave               Test Automation rules

Fill form using CSS
    [tags]                  forattr
    SetConfig               ClearKey                None
    TypeText                First input             Robot
    TypeText                Second input            QENROB
    TypeText                Cell 1 input            20022019
    TypeText                Cell 2                  Test
    TypeText                First input             ${EMPTY}
    VerifyInputValue        First input             ${EMPTY}
    TypeText                Cell 3                  Last one in this row
    TypeText                Misplaced input         I'am at wrong place!!
    ${value}                GetInputValue           field6
    ShouldBeEqual           ${value}                I'am at wrong place!!
    TypeText                Some text               I'am catching you too..
    ${value}                GetInputValue           Some text
    ShouldbeEqual           ${value}                I'am catching you too..

Use tab and enter in input text
    [tags]	PROBLEM_IN_FIREFOX
    TypeText                First input             Robot\tSecondInputText
    VerifyInputValue        Second input            SecondInputText
    TypeText                Second input            QENROB\n
    VerifyInputValue        Second input            QENROB

Use xpaths while CSS Selectors are on
    TypeText                //*[@placeholder\="username"]       Test Automation
    VerifyInputValue        //input[@placeholder\="username"]   Test Automation

Using content editable HTML elements
    [tags]                   pp
    TypeText                Editable Div            Editable One
    TypeText                Another Editable Div    Second one
    TypeText                Third Editable Div      Third
    VerifyInputValue        Editable Div            Editable One
    ${VAL}                  GetInputValue           Third Editable  partial_match=True
    ShouldBeEqual           ${VAL}                  Third

VerifyInput From Input With Label
    VerifyInputValue        Name                    Lancelot

Type Text Placeholder And Verify Input Value
    TypeText                username                Qentinel
    VerifyInputValue        xpath\=//input[@placeholder\="username"]   Qentinel
    TypeText                username                Robot
    VerifyInputValue        //*[@placeholder\="username"]       Robot

Type Text
    TypeText                row2column2             22
    VerifyInputValue        xpath\=//input[@id\="r2c2"]   22

Type Text Another Input Field To The Left
    [Tags]                  jailed
    Log                     Not implemented correctly yet
    #TypeText               row1column3             13
    #VerifyInputValue       xpath\=//input[@id\="r1c3"]   13

Type Text into Tel Type Inputbox
    [Tags]                  PROBLEM_IN_SAFARI
    SetConfig               CSSSelectors            False
    TypeText                row2column4             33
    VerifyInputValue        xpath\=//input[@id\="r2c3"]   33
    SetConfig               CSSSelectors            True

TypeText but box id delayed
    ClickText               Show inputbox
    TypeText                hiddenbox               not hidden
    VerifyInputValue        //*[@id\='hide']         not hidden

Verify Input Value Empty
    [Tags]                  jailed
    Log                     Not implemented correctly yet
    #VerifyInputValue       row1column1             ${EMPTY}

Verify Input Status Enabled
    VerifyInputStatus       row1column1             Enabled

Verify Input Status Enabled when CSS used
    VerifyInputStatus       row1column1             Enabled

Verify Input Value by WebElement instance
    TypeText                xpath\=//*[@id\="jeuda"]                park
    ${input}=               GetWebElement          xpath\=//*[@id\="jeuda"]
    VerifyInputValue        ${input}[0]            park

Verify Input Status Enabled Actually Disabled when CSS used
    Run Keyword and Expect Error       QWebValueError: The input field was disabled   VerifyInputStatus
    ...   row3column3   Enabled     timeout=2

Verify Input Status Enabled Actually Disabled
    Run Keyword and Expect Error       QWebValueError: The input field was disabled   VerifyInputStatus
    ...   row3column3   Enabled     timeout=2

Verify Input Status Disabled
    VerifyInputStatus       row3column3             Disabled

Verify Input Status Disabled when CSS Selectors are used
    VerifyInputStatus       row3column3             Disabled

Verify Input Status Disabled Actually Enabled Fail
    Run Keyword and Expect Error       QWebValueError: The input field was enabled   VerifyInputStatus
    ...   row2column2       Disabled    timeout=2

VerifyInputStatus ReadOnly
    [tags]                  ronly
    RefreshPage
    VerifyInputStatus       ronly                   readonly
    ClickElement            ronly                   tag=input
    ${message}=     Set Variable    QWebValueError: readonly attr not found
    Run Keyword and Expect Error   ${message}
    ...     VerifyInputStatus   ronly   readonly  timeout=0.2s

VerifyInputStatus enabled when ReadOnly exists
    [tags]                  ronly1
    RefreshPage
    VerifyInputStatus       ronly                   readonly
    ${message}=     Set Variable    QWebValueError: The input field was disabled
    Run Keyword and Expect Error   ${message}
    ...     VerifyInputStatus   ronly   enabled     timeout=0.2s
    ClickElement            ronly                   tag=input
    ${message}=     Set Variable    QWebValueError: readonly attr not found
    Run Keyword and Expect Error   ${message}
    ...     VerifyInputStatus   ronly   readonly  timeout=0.2s

Verify Input Handler
    [Tags]                  PROBLEM_IN_WINDOWS    PROBLEM_IN_SAFARI
    SetConfig               InputHandler            raw
    TypeText                username                Qentinel
    SetConfig               InputHandler            selenium
    TypeText                username                Rocks
    [Teardown]              SetConfig               InputHandler            selenium

Verify partial match
    ${old}=                 SetConfig               MatchingInputElement    containing input element
    VerifyInputStatus       sernam                  Enabled
    SetConfig               MatchingInputElement    ${old}

Verify search strategy
    ${old}=                 SetConfig               MatchingInputElement  //*[@placeholder\="{}"]
    VerifyInputStatus       username                Enabled
    SetConfig               MatchingInputElement  ${old}

Verify search strategy all elements
    SetConfig               MatchingInputElement  //*[@type\="{0}"]
    ${old}=                 SetConfig             AllInputElements      //input
    VerifyInputStatus       text                    Enabled                 row1column1
    SetConfig               AllInputElements      ${old}

Verify search strategy placeholders
    Run Keyword and Expect Error       ValueError: xpath has invalid number of placeholders, got 2, 0
    ...   SetConfig               MatchingInputElement       //*[@type\="{} {}"]
    Run Keyword and Expect Error       ValueError: xpath has invalid number of placeholders, got 0, 2
    ...   SetConfig               MatchingInputElement       //*[@type\="{0} {1}"]
    Run Keyword and Expect Error       ValueError: xpath has invalid number of placeholders, got 1, 1
    ...   SetConfig               MatchingInputElement       //*[@type\="{} {0}"]

Set Line Break Tab
    [Tags]                  PROBLEM_IN_WINDOWS      PROBLEM_IN_FIREFOX
    SetConfig               LineBreak               \t
    VerifyNoText            on focus
    TypeText                end-key                 dummytext
    VerifyNoText            on focus

Set Line Break Empty
    [Tags]                  PROBLEM_IN_WINDOWS      empty_line_break	PROBLEM_IN_FIREFOX
    SetConfig               LineBreak               \ue000
    VerifyNoText            on focus
    TypeText                end-key                 dummytext
    VerifyText              on focus
    RefreshPage

Set Line Break Empty 2
    [Tags]                  PROBLEM_IN_WINDOWS      empty_line_break	PROBLEM_IN_FIREFOX
    SetConfig               LineBreak               Empty
    VerifyNoText            on focus
    TypeText                end-key                 dummytext
    VerifyText              on focus
    RefreshPage

Set Line Break Empty 3
    [Tags]                  PROBLEM_IN_WINDOWS      empty_line_break	PROBLEM_IN_FIREFOX
    SetConfig               LineBreak               None
    VerifyNoText            on focus
    TypeText                end-key                 dummytext
    VerifyText              on focus
    RefreshPage

Set Line Break Empty 4
    [Tags]                  PROBLEM_IN_WINDOWS      empty_line_break	PROBLEM_IN_FIREFOX
    SetConfig               LineBreak               Null
    VerifyNoText            on focus
    TypeText                end-key                 dummytext
    VerifyText              on focus
    RefreshPage

Set Line Break None
    [Tags]                  PROBLEM_IN_WINDOWS      PROBLEM_IN_FIREFOX
    # first we need to clear the focus from previous test case
    SetConfig               LineBreak               \t
    TypeText                end-key                 dummytext
    # now that focus is cleared, we can run the test
    SetConfig               LineBreak               ${EMPTY}
    VerifyNoText            on focus
    TypeText                end-key                 dummytext
    VerifyText              on focus


Verify Closest Before SearchDirection
    SetConfig               CSSSelectors            False
    TypeText                Other:                  Zorb
    VerifyInputValue        xpath\=//*[@id\="jeuda"]  Zorb

Search Direction
    SetConfig               SearchDirection         down
    TypeText                Other:                  Qwerty
    VerifyInputValue        xpath\=//*[@id\="udjskw"]   Qwerty

Search Direction All Directions
    SetConfig               SearchDirection        left
    TypeText                LeftRight               left
    VerifyInputValue        xpath\=//*[@id\="rddf"]   left

    SetConfig               SearchDirection         right
    TypeText                LeftRight               right
    VerifyInputValue        xpath\=//*[@id\="odjdq"]  right

    SetConfig               SearchDirection        up
    TypeText                UpDown                  up
    VerifyInputValue        xpath\=//*[@id\="frtyhg"]   up

    SetConfig               SearchDirection        down
    TypeText                UpDown                  down
    VerifyInputValue        xpath\=//*[@id\="igtews"]   down

    SetConfig               SearchDirection        closest
    TypeText                Name                    Sir Robin
    VerifyInputValue        xpath\=//*[@id\="n"]      Sir Robin
    SetConfig               CSSSelectors            True

No Textbox found
    GoTo                    file://${CURDIR}/../resources/input.html
    Run Keyword And Expect Error       QWebElementNotFoundError: Unable to find*
    ...   TypeText   Lorem   foo   1   3

No Textboxes on page
    GoTo                    file://${CURDIR}/../resources/text.html
    Run Keyword And Expect Error    QWebElementNotFoundError: Unable to find*
    ...   TypeText                  HoverDropdown    Qwerty     timeout=2

Secret
    [documentation]         Test secrets handling. It is recommended to provide any secrets
    ...                     as variables outside the script.
    GoTo                    file://${CURDIR}/../resources/input.html
    # Testing purposes only
    ${SECRET}               Set Variable            sdfpv98xddv097vsdxv97
    # Recommended, secret is provided as variable OUTSIDE of the test script and version control.
    TypeSecret              end-key          Qentinel       ${SECRET}
    # Not recommended, secret is stored in script.
    TypeSecret              First input             fdfsdf98723fdkjc9vsdv222
    # Try multiple parameters
    TypeSecret              First input             223423423423423432      end-key                 1

Secret Without Debug Logs When Debugfile Option Used
    [documentation]         Test secrets when -b/--debugfile option is used.
    [Tags]                  WITH_DEBUGFILE
    GoTo                    file://${CURDIR}/../resources/input.html
    TypeSecret              First input           fdfsdf98723fdkjc9vsdv222
    TypeSecret3             First input           223423423423423432
    TypeText                Second input          View this text in debug file
    ${TextFileContent}      Get File              ${DEBUG FILE}
    Should Contain          ${TextFileContent}    QWeb.Type Secret
    Should Contain          ${TextFileContent}    QWeb.Type Secret3
    Should Contain          ${TextFileContent}    QWeb.Type Text
    Should Not Contain      ${TextFileContent}    fdfsdf98723fdkjc9vsdv22
    Should Not Contain      ${TextFileContent}    223423423423423432
    Should Contain          ${TextFileContent}    DEBUG - Preferred text: "View this text in debug file"

Test Input kw:s when traverse limit is false
    [documentation]         Find input from overly nested dom.
    [tags]                  jailed	PROBLEM_IN_FIREFOX
    ScrollText              Foobar
    Run Keyword And Expect Error    QWebElementNotFoundError: Unable to find*
    ...     TypeText               Foobar                Testi         timeout=0.5s
    Run Keyword And Expect Error    QWebElementNotFoundError: Unable to find*
    ...     VerifyInputValue       Foobar                ${EMPTY}      timeout=0.5s
    TypeText                Foobar                 Qentinel     limit_traverse=False
    VerifyInputValue        Foobar                 Qentinel     limit_traverse=False

Test ClearKey Parameter
    [documentation]         Use optional clear key
    [tags]                  PROBLEM_IN_FIREFOX      PROBLEM_IN_MACOS
    TypeText                The Brave             Kalakalle
    VerifyInputValue        The Brave             Kalakalle
    TypeText                The Brave             Kalakalle     clear_key={NULL}
    VerifyInputValue        The Brave             KalakalleKalakalle
    TypeText                The Brave             Kalakalle     clear_key={CONTROL + A}
    VerifyInputValue        The Brave             Kalakalle

PressKey test hotkeys
    [documentation]         Use keyboard shortcuts with press key
    [tags]                  PROBLEM_IN_MACOS
    RefreshPage
    TypeText                The Brave             Kalakalle
    VerifyInputValue        The Brave             Kalakalle
    PressKey                The Brave             {CONTROL + A}
    PressKey                The Brave             {CONTROL + C}
    PressKey                The Brave             {DELETE}
    VerifyInputValue        The Brave             ${EMPTY}
    PressKey                username              {CONTROL + V}
    VerifyInputValue        username              Kalakalle

PressKey test hotkeys - Mac
    [documentation]         Use keyboard shortcuts with press key
    [tags]                  PROBLEM_IN_WINDOWS    PROBLEM_IN_LINUX
    RefreshPage
    TypeText                The Brave             Kalakalle
    VerifyInputValue        The Brave             Kalakalle
    PressKey                The Brave             {COMMAND + A}
    PressKey                The Brave             {COMMAND + C}
    PressKey                The Brave             {BACKSPACE}
    VerifyInputValue        The Brave             ${EMPTY}
    PressKey                username              {COMMAND + V}
    VerifyInputValue        username              Kalakalle

GetInputValue get substring
    TypeText                username                Write some random words and number 25.11.2019
    ${substring}            GetInputValue           username    between=some???words
    ShouldBeEqual           ${substring}            random
    ${substring}            GetInputValue           username    from_start=5
    ShouldBeEqual           ${substring}            Write
    ${substring}            GetInputValue           username    from_end=6  float=True
    ShouldBeEqual           ${substring}            ${1.2019}

GetInputValue use blind flag
    [tags]                  blind
    TypeText                username                ${EMPTY}
    Run Keyword And Expect Error    QWebValueErr*
    ...     GetInputValue       username            timeout=1
    ${VALUE}                GetInputValue           username    blind=True
    ShouldBeEqual           ${EMPTY}                ${VALUE}

GetInputValue use config BlindReturn
    [tags]                  blind
    TypeText                username                ${EMPTY}
    Run Keyword And Expect Error    QWebValueErr*
    ...     GetInputValue       username            timeout=1
    SetConfig               BlindReturn             True
    ${VALUE}                GetInputValue           username
    ShouldBeEqual           ${EMPTY}                ${VALUE}
    SetConfig               BlindReturn             False

TypeText to ReadOnly input using ClickToFocus
    [tags]                  readonly
    Run Keyword And Expect Error    QWebValueError: Expected value*
    ...     TypeText       ronly    Fisherman   check=True      timeout=0.5s
    SetConfig              ClicktoFocus             True
    TypeText               ronly                    Average Joe
    VerifyInputValue       ronly                    Average Joe
    SetConfig              ClicktoFocus             False

TypeTexts and VerifyInputValues
    # With dict
    [tags]	PROBLEM_IN_FIREFOX
    ${data}=             Create Dictionary      Name:=idkfa  username=iddqd  Second input:=idclip
    TypeTexts            ${data}
    VerifyInputValues    ${data}

    # With text file
    RefreshPage
    TypeTexts            test4.txt
    VerifyInputValues    test4.txt

TypeTexts and VerifyInputValues fail
    [tags]	PROBLEM_IN_FIREFOX    PROBLEM_IN_SAFARI
    ${message}=  Set Variable  QWebValueError: Unknown input value. Text file or*
    Run Keyword And Expect Error        ${message}
    ...    VerifyInputValues    bad_parameter.xlsx
    Run Keyword And Expect Error        ${message}
    ...    TypeTexts    gfhfghkojfghoigfh298354234

TypeText multiple anchors fail
    [Documentation]         Use non-unique anchor to find input and expect failure
    [Tags]                  multipleanchors
    ${message}=             Set Variable    QWebValueError: Text "anchor" matched * Needs to be unique
    Run Keyword And Expect Error    ${message}
    ...    TypeText    Address    Null pointer street 0x0    anchor    timeout=2s

TypeText multiple anchors enabled
    [Documentation]         Use non-unique anchor to find input successfully
    [Tags]                  multipleanchors
    SetConfig               MultipleAnchors    True
    VerifyNoText            Backstreet alley 10
    TypeText                Address    Backstreet alley 10    anchor
    # Verify that text is in the first exact match
    VerifyInputValue        Address    Backstreet alley 10    3    timeout=2s
    VerifyNoText            My way or highway 66
    TypeText                Address    My way or highway 66    anchortext
    # Verify that text is in the first partial match
    VerifyInputValue        Address    My way or highway 66    1    timeout=2s
    [Teardown]              SetConfig    MultipleAnchors    False
