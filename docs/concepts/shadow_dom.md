# Shadow DOM Support

Modern web applications (especially those built with Web Components) often use **Shadow DOM** to encapsulate styles and markup.

## The Challenge

Elements inside a Shadow Root are isolated from the main document. Standard automation strategies (like `document.querySelector` or global XPaths) usually hit a brick wall—they simply cannot "see" inside the shadow root.

## The QWeb Solution

QWeb can pierce through Shadow DOM boundaries, but you must enable this feature explicitly because it changes the search scope.

### Enabling Support

Use `SetConfig` to turn on Shadow DOM traversal.

```robotframework
*** Test Cases ***
Interact with Shadow DOM
    # Enable Shadow DOM support
    SetConfig      ShadowDOM    True
    
    OpenBrowser    chrome://settings    chrome
    
    # Now QWeb can see elements inside shadow roots
    VerifyText     Clear browsing data
```

## Important Limitation

Because Shadow DOMs are designed to be isolated, **XPaths do not work** inside them.

When testing Shadow DOM elements, use QWeb's native locators or CSS locators:

*   ✅ `ClickText`, `VerifyText`
*   ✅ `ClickItem`, `VerifyItem` (attributes)
*   ✅ `ClickElement css\=...` (basic selectors, see below)
*   ❌ `ClickElement xpath\=...` (Will fail)

```robotframework
# GOOD
ClickText      Save Settings
ClickElement   css\=button#save

# BAD (Will not find element inside Shadow DOM)
ClickElement   xpath\=//button[@id\='save']
```

### CSS locators in Shadow DOM

With `ShadowDOM` on, `css\=` locators search the main document and every **open** shadow root. Each tree is searched on its own, so a single selector can't cross a shadow boundary:

```robotframework
SetConfig      ShadowDOM    True
ClickElement   css\=button.save                 # finds the button inside a component's shadow root
ClickElement   css\=button:has-text("Save")     # text filters work too
VerifyNoElement    css\=my-component button.save    # doesn't match: crosses the shadow boundary
```

*   Closed shadow roots, `::part()` and `::slotted()` are not supported.
*   Matches in the main document come first, then matches in shadow roots in document order; `index` counts in that order.