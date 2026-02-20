# Checkboxes & Toggles

QWeb provides specific keywords to handle checkboxes and toggle switches, allowing you to interact with them by their label and verify their state (On/Off) without inspecting HTML.

## 1. Interacting with Checkboxes

While you *can* just use `ClickText` to toggle a box, it is often safer to **enforce** a specific state.

### `ClickCheckbox` (Enforce State)
This keyword checks the current state before clicking.

*   If you say `On` and it is already checked, QWeb does nothing.
*   If you say `On` and it is unchecked, QWeb clicks it.

```robotframework
# Syntax: ClickCheckbox    Label    State (On/Off)

# Ensure "Subscribe" is checked (clicks only if needed)
ClickCheckbox    Subscribe    On

# Ensure "Marketing Emails" is unchecked
ClickCheckbox    Marketing Emails    Off
```

### `ClickText` (Simple Toggle)
Use this only if you want to "blindly" toggle the value regardless of its current state.

```robotframework
# Toggles the value (On -> Off, or Off -> On)
ClickText    I agree to terms
```

## 2. Verifying State (`VerifyCheckbox`)

Rather than checking DOM attributes directly via XPath (for example inspecting checked, CSS classes, or aria-checked), use VerifyCheckbox. The keyword encapsulates the logic for determining checkbox state and reduces dependency on implementation details.

```robotframework
# Verify that "Subscribe" is currently checked
VerifyCheckbox    Subscribe    On

# Verify that "Old Newsletter" is NOT checked
VerifyCheckbox    Old Newsletter    Off
```


