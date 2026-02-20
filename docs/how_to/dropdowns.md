# Handling Dropdowns

Dropdowns in web applications generally fall into two categories: standard HTML `<select>` lists and modern, custom-styled "Div" dropdowns. QWeb handles each differently.

## 1. Standard Dropdowns (`<select>`)

For traditional HTML dropdowns, use the dedicated `DropDown` keyword.

```robotframework
# Syntax: DropDown    Label    Value
DropDown    Country    Finland
```

### Supported Dropdown Keywords

| Keyword | Purpose |
|----------|----------|
| `DropDown` | Select a value from a standard `<select>` dropdown |
| `GetDropDownValues` | Returns all option values from a standard `<select>` dropdown |
| `GetSelected` | Gets the currently selected option |
| `VerifyOption` | Verify a specific option exists |
| `VerifyNoOption` | Verify a specific option does not exist |
| `VerifySelectedOption` | Verify the currently selected option |

!!! failure "Critical Limitation"
    The above Dropdown keywords **ONLY** work on standard HTML `<select>` tags.
    
    If you try to use `DropDown` on a modern, custom-styled dropdown (which is actually a `<div>` or `<ul>`), QWeb will fail to find it. In those cases, use the **Modern Strategy** below.

## 2. Modern / Custom Dropdowns

Most modern frameworks (React, Angular, Vue) use custom components to render dropdowns. To QWeb, these are just text and buttons.

**Strategy:** Interact with them exactly like a user would.

1.  **Click** the dropdown label/box to open it.
2.  **Click** the text of the option you want.

```robotframework
*** Test Cases ***
Select From Custom Dropdown
    # 1. Click the "Role" box to expand the list
    ClickText    Role
    
    # 2. Click the option "Administrator" inside the list
    ClickText    Administrator
```

### Verification
Since there is no `<option>` tag to check, simply verify that the text on the screen has updated.

```robotframework
# Verify "Administrator" is now visible in the box
VerifyText    Administrator
```

## Summary

Standard `<select>` dropdown:

- Use `DropDown`
- Use `VerifyOption` / `VerifyNoOption`

Modern custom dropdown:

- Use `ClickText`
- Use `VerifyText`
- Treat it like a normal interactive component

