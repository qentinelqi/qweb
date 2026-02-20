# Writing Your First Test

QWeb relies on **Robot Framework**, meaning your tests will be structured in `.robot` files using a simple, tabular syntax.

!!! tip "QWeb can be used directly from Python as well. See: [Python usage](../how_to/python.md) ."

## The Basic Structure

A standard QWeb test file consists of two main sections:

1.  **`*** Settings ***`**: Where you import the `QWeb` library.
2.  **`*** Test Cases ***`**: Where you define your test steps.

### Example: User Login

Here is a complete, runnable example of a login test. Notice how the code reads almost exactly like a manual test case.

```robotframework
*** Settings ***
Library    QWeb

*** Test Cases ***
User Can Log In
    OpenBrowser    https://example.com    chrome
    TypeText       Email       demo@example.com
    TypeText       Password    changeme
    ClickText      Sign in
    VerifyText     Dashboard

```

### Breaking It Down

Let's look at what is happening line-by-line:

#### 1. Opening the Browser
   
```robotframework
OpenBrowser    https://example.com    chrome
```

* What it does: Opens a new browser instance to the specified URL.
*  Browsers: Common options include chrome, firefox, edge, or safari.
*  Drivers: Remember, QWeb handles the drivers automatically, so this just works!

#### 2. Interacting with Inputs
   
```robotframework
TypeText       Email       demo@example.com
```

* The Magic: You don't need to find the specific `<input id="email">` tag.
* How it works: QWeb looks for the visible text "Email" (a label or placeholder) and automatically types into the input field associated with it.

#### 3. Clicking Elements

```robotframework   
ClickText      Sign in
```

* What it does: Scans the page for the visible text "Sign in" and clicks it.
* Versatility: This works on `<button>, <a> links, or even <div>` elements that look like buttons.

#### 4. Verifying Results
   
```robotframework   
VerifyText     Dashboard
```

* Assertion: This checks if the text "Dashboard" is visible on the screen.
* Automatic Waits: If the page takes a few seconds to load, QWeb will automatically retry finding this text for up to 10 seconds (default) before failing. You don't need to add Sleep!

### The "Text-First" Philosophy

The core philosophy of QWeb is to test what the user sees.

* Avoid: Complex XPaths like //div[@id='main']/div/button (unless absolutely necessary).
* Prefer: ClickText    Save

This makes your tests resilient. If the developer changes the underlying HTML ID but the button still says "Save", your test will pass.