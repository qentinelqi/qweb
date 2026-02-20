# Configuration

QWeb is designed to work "out of the box" for most websites. However, you can customize its behavior globally using the `SetConfig` keyword.

## Usage

Settings changed with `SetConfig` stay in effect until you change them back or the test execution ends.

```robotframework
# Syntax: SetConfig    Parameter    Value
SetConfig    DefaultTimeout    30s
```

## Available Settings
<!-- The div style below is just a hack to keep first column in one line. Without it,
MatchingInputElement had "t" in new line. -->
| <div style="width:170px">Parameter | Default | Description |
| :--- | :--- | :--- |
| **`ActiveAreaXpath`** | | Set search strategy for element search. |
| **`AllInputElements`** | | Set search strategy for element search. |
| **`BlindReturn`** | `False` | Return value without waiting. If `True`, returns empty string instead of failing if input is empty/not found immediately. |
| **`CaseInsensitive`** | `False` | Allow case insensitive search when partial match is used. |
| **`CheckInputValue`** | `False` | Check that typed value is stored correctly after `TypeText`. If mismatch, retries typing. |
| **`ClearKey`** | *Default* | Key used to clear previous value before typing (e.g., `{BACKSPACE}`). Default uses WebDriver's clear method. |
| **`ClickToFocus`** | `False` | If `True`, sets focus by clicking the input field before typing. |
| **`CssSelectors`** | `True` | Use CSS selectors as a fallback strategy for finding elements (e.g., inputs without placeholders). |
| **`DefaultDocument`** | `True` | Automatically switch back to the default frame after each keyword. Set to `False` for manual frame handling. |
| **`DefaultTimeout`** | `10s` | How long to wait for an element to appear before failing the test case. |
| **`Delay`** | `0s` | Wait time added *before* every keyword execution. Useful for debugging or demos. |
| **`DoubleClick`** | `False` | If `True`, performs a double-click action for all `Click*` keywords. |
| **`HandleAlerts`** | `True` | Automatically handle/dismiss unexpected browser alerts. |
| **`HighlightColor`** | `blue` | Sets the color of the highlight rectangle when `SearchMode` is active. (e.g., `red`, `orange`, `green`). |
| **`InputHandler`** | `selenium` | Method to input text: `selenium` (standard), `raw` (pyautogui), or `javascript`. |
| **`InViewport`** | `False` | If `True`, elements outside the current viewport are considered invisible/not found. |
| **`IsModalXPath`** | | Set search strategy for element search regarding modal dialogs. |
| **`LineBreak`** | `\ue004` | Key to send after typing text. Default is `Tab` (\ue004). |
| **`LogMatchedIcons`** | `False` | If `True`, highlights where an icon was found and adds a screenshot to the logs. |
| **`LogScreenShot`** | `True` | Adds a screenshot of the failure to the logs. Set to `False` to disable failure screenshots. |
| **`MatchingInputElement`** | | Set search strategy for element search. |
| **`MultipleAnchors`** | `False` | If `True`, accepts non-unique anchors and selects the first match. |
| **`OffsetCheck`** | `True` | Check if element has offset (dimensions). Elements with no offset are considered invisible. |
| **`OSScreenshots`** | `False` | Use operating system functionalities instead of Selenium to take screenshots. |
| **`PartialMatch`** | `True` | Accept partial matches for text search (e.g., "Log" matches "Login"). Set to `False` for exact match only. |
| **`RenderWait`** | `200ms` | Time to wait for DOM to stabilize before interacting. Ensures page is not still rendering. |
| **`RetinaDisplay`** | *Auto* | Manually set if current monitor is Retina (`True`) or not (`False`). |
| **`RetryInterval`** | `5s` | Timeout to wait before re-trying in `ClickUntil` / `ClickWhile` keywords. |
| **`RunBefore`** | `None` | A keyword to run before *every* interaction keyword. Useful for waiting for custom spinners. |
| **`ScreenShotType`** | `screenshot`| Defines logging format: `screenshot`, `html` (source), or `all`. |
| **`SearchDirection`** | `closest` | Relative direction for element search (`closest`, `up`, `down`, `left`, `right`). Append `!` for strict mode (e.g., `down!`). |
| **`SearchMode`** | `draw` | Visual feedback. `draw` highlights elements with a border. `debug` blinks them. `None` disables it. |
| **`ShadowDOM`** | `False` | If `True`, extends search to include elements inside Shadow DOMs. |
| **`SpinnerCSS`** | `none` | CSS selector for loading indicators. If found, QWeb waits for them to disappear before acting. |
| **`StayInCurrentFrame`** | `False` | Only search from the current frame. Disables automatic frame traversal. |
| **`VerifyAppAccuracy`** | `0.9999` | Threshold for image similarity in `VerifyApp` keyword. |
| **`Visibility`** | `True` | If `False`, QWeb will interact with invisible/hidden elements. |
| **`WaitStrategy`** | `enhanced` | Synchronization strategy: `enhanced` (checks network/DOM) or `legacy` (jQuery based). |
| **`WindowFind`** | `False` | If `True`, simulates `CTRL+F` behavior to find text instead of DOM search. |
| **`WindowSize`** | `Full screen`| Sets the size of the browser window. |
| **`XHRTimeout`** | `30s` | Maximum wait time for the page to load (XHR/Network idle). |

!!! tip "Refer to the Set Config keyword documentation for the latest details and examples for each configuration parameter."

## Common Use Cases

### 1. Handling Slow Environments
If your test environment is consistently slow, increase the global timeout at the start of your suite.

```robotframework
*** Test Cases ***
Setup Suite
    SetConfig    DefaultTimeout    60s
```

### 2. Testing "Invisible" Inputs
Some file uploaders or modern frameworks hide the actual `<input>` tag.

```robotframework
# Allow QWeb to interact with hidden elements
SetConfig    Visibility    False
UploadFile   Upload        C:/data/image.png
SetConfig    Visibility    True
```

### 3. Debugging Layouts
If QWeb is clicking the wrong "Edit" button, you can visualize the search and slow it down.

```robotframework
# Draw a red box around elements and wait 1s before clicking
SetConfig    HighlightColor    Red
SetConfig    Delay             1s
```

### 4. Handling Spinners
To automatically wait for a custom loading animation (e.g., a spinning wheel with class `loader`):

```robotframework
SetConfig    SpinnerCSS    .loader
# QWeb will now automatically wait for ".loader" to disappear before clicking anything
ClickText    Submit
```