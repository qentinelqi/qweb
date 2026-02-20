# Handling Frames

One of the most frustrating aspects of traditional web automation is dealing with **iFrames** (Inline Frames).

In standard Selenium or other libraries, if a button is inside an `<iframe>`, you must explicitly tell the driver to "switch focus" to that frame before you can interact with it. If you forget, your test fails, even if the button is clearly visible on the screen.

## The QWeb Approach

QWeb handles frames **automatically**.

When you execute a keyword like `ClickText`, QWeb scans the main page **and** traverses through any iFrames it encounters to find your target.

### Usage

**You do nothing.** Just write your test as if the page were a single, flat document.

```robotframework
*** Test Cases ***
Interact With Frame
    OpenBrowser    https://example.com/page-with-frames    chrome
    
    # This element is in the main window
    VerifyText     Main Menu
    
    # This element is inside <iframe id="payment">
    # QWeb finds it automatically without 'Select Frame'
    TypeText       Card Number     1234-5678
```