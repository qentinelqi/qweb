# Forms & Inputs in QWeb

Form handling is the most common automation task.  
QWeb simplifies this using Smart Locators, which associate visible text, placeholders, and attributes with their corresponding input fields.

The guiding principle:

> Interact with inputs like a user would — not by inspecting DOM structure.

## 1. Standard Text Fields (`TypeText`)

```robot
TypeText    Email    demo@example.com
```

`TypeText` is the primary keyword for entering text into input fields.

QWeb automatically resolves the correct input field using:

- Placeholder text
- Closest visible label
- Attribute values (`id`, `name`, `title`, etc.) of an input element
- Direct XPath (when prefixed with `xpath=` or `//`)

Examples:

```robot
TypeText    First Name    John
TypeText    Search...     Robot Framework
TypeText    submit-query  Robot Framework
TypeText    xpath\=//input[@name='q']    Robot Framework
```

## 2. Default Typing Behavior

QWeb simulates realistic form interaction, not just raw keystrokes.

### 2.1 Field Is Cleared by Default

Before typing, QWeb clears the field automatically.

This ensures:

- Old values are removed
- No leftover characters remain
- Tests remain deterministic

Override per keyword:

```robot
TypeText    Comment    Additional text    clear_key={NULL}
```

Override globally:

```robot
SetConfig   ClearKey     {CONTROL + A}  # Select all and overwrite
```

### 2.2 Automatic TAB After Typing

By default, QWeb sends a TAB after typing to move focus to the next field.

This triggers:

- OnBlur validation
- Auto-save logic
- Field formatting
- Client-side validation


This setting can be changed globally:

```robot
SetConfig   LineBreak    \ue007    # Enter key
```

Use this carefully, as some applications rely on blur events.

## 3. Special Characters in Typed Text

QWeb interprets certain escape sequences inside the typed string.

### `\n` — New Line (Enter)

```robot
TypeText    Message    Hello\nWorld
```

Equivalent to pressing Enter between lines.

Useful for:
- Textareas
- Chat inputs
- Submitting forms via Enter

### `\t` — Tab Key

```robot
TypeText    Field    Value\t
```

Simulates pressing the TAB key explicitly.

Note:

- QWeb already sends TAB by default (unless disabled).
- Use `\t` only when explicit control is required.

## 4. Sensitive Data (`TypeSecret`)

Never use `TypeText` for passwords or secrets.

```robot
TypeSecret    Password    MySuperSecret123!
```

Why?

- Value is masked in Robot logs
- Prevents credentials from appearing in reports

## 5. Verifying Input State

### `VerifyInputValue`

```robot
VerifyInputValue    Email    demo@example.com
```

Ensures the field contains the expected value.

### `GetInputValue`

```robot
${value}=    GetInputValue    Email
```

Reads the current value.

Useful for:

- Comparing before/after changes
- Extracting generated IDs
- Validating computed fields

### `VerifyInputStatus`

```robot
VerifyInputStatus    Email    enabled
VerifyInputStatus    Email    disabled
```

Checks whether the field is interactable.

### `VerifyInputElement`

```robot
VerifyInputElement    Email
```

Confirms the input exists.

## 6. Ambiguous Forms

If multiple inputs share the same label:

```robot
TypeText    Name    John Doe    anchor=Shipping Address
TypeText    Name    Jane Doe    anchor=Billing Address
```

Anchors restrict search context.

## 7. Directional Search Strategy (`SetConfig`)

In structured layouts (for example, labels always above inputs):

```robot
SetConfig    SearchDirection    down

TypeText     First Name    John
TypeText     Last Name     Doe

SetConfig    SearchDirection    closest
```

Available directions:

- `closest` (default)
- `up`
- `down`
- `left`
- `right`
- `up!`
- `down!`
- `left!`
- `right!`

!!! note "Strict Mode"
    Search modes ending with ! enable Strict Mode.
    In strict mode, the element must be found exactly in the specified direction.
    If not found there, the search fails. No fallback matching is performed.
    Strict mode applies only to text-based searches (e.g. VerifyText, ClickText).

## 8. Hidden or Dynamic Inputs

QWeb interacts with visible elements by default.

If necessary:

```robot
SetConfig    Visibility    False
```

Use cautiously — hidden inputs are typically not user-interactable.

## 9. Related Input Keywords

| Keyword | Purpose |
|----------|----------|
| `TypeText` | Enter text into input fields |
| `TypeSecret` | Enter masked sensitive data |
| `VerifyInputValue` | Verify current value |
| `GetInputValue` | Retrieve value |
| `VerifyInputStatus` | Check enabled/disabled state |
| `VerifyInputElement` | Confirm input exists |

## Design Principles

1. Prefer visible text over XPath.
2. Let QWeb handle field state instead of manual DOM assertions.
3. Keep default clearing and TAB behavior unless you have a reason to change it.
4. Validate behavior, not HTML implementation.
5. Use `TypeSecret` for anything sensitive.
