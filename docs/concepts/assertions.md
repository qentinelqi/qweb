# Assertions & Logic

In QWeb, interacting with the application state is divided into four distinct categories of keywords. Choosing the right one is critical for test stability and logic.

## 1. Hard Assertions (`Verify...`)

**Purpose:** Enforce that an element must exist.
**Behavior:** If the element is not found within the timeout, the **test fails** immediately.

Use these for your main acceptance criteria.

```robotframework
# The test will STOP here if "Welcome" is not visible
VerifyText     Welcome to your dashboard

# You can also verify attributes (like tooltips)
VerifyItem     Shopping Cart
```

## 2. Negative Assertions (`VerifyNo...`)

**Purpose:** Enforce that an element must **not** exist.
**Behavior:** If the element *is* found, the **test fails**.

This is the correct way to ensure an action (like "Delete") was successful.

```robotframework
# Correct: Fails if "Item 1" is still visible
VerifyNoText   Item 1

# Incorrect: Do NOT use "VerifyText" inside a "Run Keyword And Expect Error" block.
# Use the dedicated VerifyNo keyword instead.
```

## 3. Boolean Checks (`Is...`)

**Purpose:** Check if an element exists without stopping execution.
**Behavior:** Returns `True` or `False`.
**Crucial Note:** These keywords **never fail the test**, even if the element is missing. They are purely for conditional logic.

Use these for handling optional steps (e.g., closing a promo banner that might not always appear).

```robotframework
${popup_visible}=    IsText    Accept Cookies

IF    ${popup_visible}
    ClickText    Accept Cookies
END
```

## 4. Retrieving Data (`Get...`)

**Purpose:** Extract information from the page into a variable for later use.
**Behavior:** Returns a value (string, integer, or list) but generally does not enforce success/failure.

Use these when you need to calculate results or pass data to another keyword.

```robotframework
# Example: Get the value currently typed in the "Email" field
${current_email}=    GetInputValue    Email

# Example: Count how many times the text "Error" appears
${error_count}=      GetText          Error

# Example: Get text from a specific table cell
${row_text}=         GetCellText      ${row_index}    Description
```

## Summary of Keywords

| Strategy | Enforce Presence (Fail if missing) | Enforce Absence (Fail if present) | Check Status (No Fail, Return Bool) | Retrieve Data (Return Value) |
| :--- | :--- | :--- | :--- | :--- |
| **Text** | `VerifyText` | `VerifyNoText` | `IsText` | `GetText` |
| **Item** | `VerifyItem` | `VerifyNoItem` | `IsItem` | `GetInputValue` |
| **Element** | `VerifyElement` | `VerifyNoElement` | `IsElement` | `GetElementAttribute` |

## Best Practices

*   **Avoid `Run Keyword And Return Status`:** In standard Robot Framework, you often wrap keywords to check for success. In QWeb, simply use the `Is...` keywords—they are faster and cleaner.
*   **Trust the Waits:** All `Verify` keywords automatically wait for the element to appear (or disappear). You do not need to add `Sleep` before an assertion.
