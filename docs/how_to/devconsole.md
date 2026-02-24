# Working with Browser Console

This page explains how to capture and verify browser console messages and JavaScript exceptions using QWeb's BiDi-powered keywords. You will learn how to enable BiDi, start and stop console capture, retrieve messages, and verify there are no errors.
s
!!! warning "BiDi Support is Evolving"
    **BiDi is a modern browser automation protocol, but support is still evolving.**
    Only enable BiDi when you need to use keywords that require it (such as console capture). Keeping BiDi enabled at all times is not recommended, as browser and Selenium support may impact stability and compatibility.
    For now, we recommend creating individual tests for features that require BiDi to be enabled, rather than enabling it globally for all tests.

## What is BiDi?

BiDi (Bidirectional) is a new browser automation protocol that allows advanced features like real-time console message capture. QWeb supports BiDi for Chrome, Edge, and Firefox (with recent Selenium and browser versions).

## Enabling BiDi

To use console capture keywords, you must enable BiDi when opening the browser. This is done by setting the `bidi` argument to `True` in the `Open Browser` keyword:

```robotframework
Open Browser    https://example.com    chrome    bidi=True
```

## Capturing Console Messages

To start capturing console messages and JavaScript exceptions, use:

```robotframework
StartConsoleCapture
```

- Only the last 1000 messages of each type are kept (older messages are overwritten).
- Messages are cleared when you close all browsers or call `StopConsoleCapture`.

## Retrieving Console Messages

Use `GetConsoleMessages` to retrieve captured messages. You can filter by log level, source, or substring:

```robotframework
${all}=       GetConsoleMessages
${errors}=    GetConsoleMessages    level=error
${console}=   GetConsoleMessages    level=error    source=console
${js}=        GetConsoleMessages    level=error    source=js
${network}=   GetConsoleMessages    contains=Network
```

- **level**: all, debug, info, warn, error, log (aliases: warning → warn, err → error)
- **source**: "console" (browser console), "js" or "exception" (JavaScript exceptions)
- **contains**: substring filter (case-insensitive)

## Verifying No Console Errors

To fail the test if any error-level messages or JS exceptions are present:

```robotframework
VerifyNoConsoleErrors
VerifyNoConsoleErrors    source=console
VerifyNoConsoleErrors    source=js
```

## Stopping Console Capture

To stop capturing and clear all stored messages for the session:

```robotframework
StopConsoleCapture
```

!!! note "Messages are cleared on stop" 
    Use `GetConsoleMessages` or `VerifyNoConsoleErrors` **before** stopping capture if you need to access the messages. Messages are cleared on stop.

## Example

```robotframework
*** Settings ***
Library    QWeb

*** Test Cases ***
Capture And Check Console
    Open Browser    https://example.com    chrome    bidi=True
    StartConsoleCapture
    # ... perform actions that may trigger console messages ...
    ${errors}=    GetConsoleMessages    level=error
    Log    ${errors}
    VerifyNoConsoleErrors
    StopConsoleCapture
    Close All Browsers
```

## Related Keywords

- `StartConsoleCapture`
- `GetConsoleMessages`
- `VerifyNoConsoleErrors`
- `StopConsoleCapture`

See the [reference/keywords.md](../reference/keywords.md) for full details.
