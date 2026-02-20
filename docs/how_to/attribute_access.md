## Working with Attributes

Sometimes validation requires checking a specific HTML attribute.

QWeb provides:

- `GetAttribute`
- `VerifyAttribute`

Use them when attribute-level verification is necessary.

---

## 1. Reading an Attribute (`GetAttribute`)

```robot
${value}=    GetAttribute    Login Button    disabled
```

Returns the value of the specified attribute.

Useful for:

- `aria-*` attributes
- Custom `data-*` attributes
- Accessibility checks
- Dynamic state flags

---

## 2. Verifying an Attribute (`VerifyAttribute`)

```robot
VerifyAttribute    Login Button    disabled    true
```

Asserts that the attribute has the expected value.

---

## 3. Understanding `element_type`

When using XPath as a locator, QWeb directly targets the element:

```robot
GetAttribute    xpath\=//button[@id='login']    disabled
```

In this case, `element_type` is not needed because the element is explicitly defined.

However, when using text-based or attribute-based smart locators, QWeb may need help determining which element type you intend to target.

Example:

```robot
GetAttribute    Login    disabled
```

If multiple elements contain the text "Login" (button, label, span, etc.), QWeb must determine the correct element.

You can explicitly guide it using `element_type`:

```robot
GetAttribute    Login    disabled    element_type=button
```

Common `element_type` values:

- `text`
- `button`
- `input`
- `checkbox`
- `dropdown`

Use `element_type` when:

- The locator text is ambiguous
- Multiple element types match the same visible text
- You need precise targeting without switching to XPath

---

## 4. When NOT to Use Attribute Checks

Many common scenarios already have dedicated keywords.

Instead of:

```robot
VerifyAttribute    Country    value    Finland
```

Prefer:

```robot
VerifyOption    Country    Finland
```

Instead of checking `checked` manually:

```robot
VerifyCheckbox    Accept Terms    on
```

Instead of checking input value via attribute:

```robot
VerifyInputValue    Email    demo@example.com
```

Dedicated keywords are more stable because they validate behavior rather than raw DOM attributes.

---

## 5. Avoid Tight Coupling to Implementation Details

Attribute checks couple your test to internal HTML structure.

Use them when:

- No higher-level keyword exists
- You are validating accessibility attributes
- You are testing dynamic component state
- You explicitly need DOM-level validation

Prefer behavior-level verification whenever possible.

### 6. Advanced: Using `GetWebElement`

The `GetWebElement` keyword follows the same locator logic as *attribute* keywords.

- If you use XPath, the exact element is returned.
- If you use a smart locator (text/attribute-based), `element_type` may be required for disambiguation.

Example using XPath:

```robot
${elem}=    GetWebElement    //*[@class\="icon_indicator"]
${color}=   Evaluate    $elem.value_of_css_property("color")
Log    ${color}
```

`GetWebElement` returns a Selenium `WebElement` instance, which allows direct interaction using Selenium methods via `Evaluate`.

This is useful when:

- You need to access CSS properties
- You need low-level DOM interaction
- No dedicated QWeb keyword exists

---

### Important: Return Type Behavior

When using XPath:

```robot
${elem}=    GetWebElement    //*[@id='login']
```

A single `WebElement` is returned.

When using smart locators with `element_type`:

```robot
${elems}=    GetWebElement    Login    element_type=button
```

A list of matching `WebElement` objects is returned.

You must handle it accordingly:

```robot
${first}=    Evaluate    $elems[0]
```

---

### Best Practice

Use `GetWebElement`, `GetAttribute` or `VerifyAttribute` only when necessary.
These keywords are powerful, but they bypass much of QWeb’s abstraction layer.

- XPath → no `element_type` needed.
- Smart locator → use `element_type` when disambiguation is required.
- Prefer dedicated verification keywords over manual attribute checks.
- Use attribute verification to support behavior validation — not replace it.

