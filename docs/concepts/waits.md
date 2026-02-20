# Smart Wait Strategies

One of the most common causes of "flaky" automation is improper waiting. Scripts often fail because they try to click a button before it has fully loaded.

QWeb solves this with a robust **Auto-Retry** mechanism.

## How it Works

You generally do not need to tell QWeb to "wait" for an element.
When you run a keyword like `ClickText`, QWeb enters a retry loop:

1.  **Search:** It looks for the text on the screen.
2.  **Action:** If found, it clicks immediately.
3.  **Retry:** If *not* found, it waits a split second and tries again.
4.  **Fail:** It repeats this until the **Timeout** is reached (Default: 10 seconds). Only then does it fail.

## Configuration

### Global Timeout
The default 10-second timeout works for most modern apps. However, if you are testing a slow legacy system or a heavy environment, you can increase this globally at the start of your test.

```robotframework
*** Test Cases ***
Configure Environment
    # Set default wait to 30 seconds for all keywords
    SetConfig      DefaultTimeout    30
    
    OpenBrowser    https://slow-app.example.com    chrome
    VerifyText     Loaded successfully    # Will now wait up to 30s
```

### Per-Keyword Timeout
Sometimes you expect a specific action to take longer (e.g., generating a report), or you want to fail faster if something isn't there immediately. You can override the timeout for a single line using the `timeout` argument.

```robotframework
# Wait up to 60 seconds just for this step
VerifyText     Report Generated    timeout=60

# Fail quickly (after 3 seconds) if this is not found
VerifyText     Popup Message       timeout=3
```

## The "Anti-Sleep" Rule

!!! danger "Avoid using `Sleep`"
    In traditional automation, you might see code like:
    ```robotframework
    Sleep          5s
    ClickElement   //button
    ```
    **Avoid this in QWeb.** Hard-coded sleeps make your test suite slow. If the button loads in 1 second, your test still waits for 5, wasting 4 seconds every time.

Instead, rely on `Verify*` keywords and adjust the max wait time with `timeout` argument necessary.

## Timeout vs. Delay

QWeb offers two arguments that look similar but behave very differently.

| Argument | Behavior | Recommendation |
| :--- | :--- | :--- |
| `timeout=10` | Waits **up to** 10s. Proceeds immediately if found. | ✅ **Preferred** |
| `delay=10` | **Always** waits 10s before even looking. | ❌ Avoid |

**When to use `delay`?**
Only use `delay` if you have a UI animation that "bounces" or fades in, and you need to ensure it has settled before interacting.

```robotframework
# Waits 2 seconds for animation to settle, then clicks
ClickText    Submit    delay=2
```