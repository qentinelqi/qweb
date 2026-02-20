# Locator Strategies

QWeb is designed to be **text-first**. Unlike traditional automation that relies heavily on HTML structure (IDs, Classes, XPaths), QWeb encourages you to interact with elements the way a human user does: by reading the screen.

To write reliable and maintainable tests, follow this hierarchy of strategies:

## 1. Text Locators (Preferred)
 
**Keywords:** `ClickText`, `VerifyText`, `HoverText`

The most robust way to locate an element is by its visible text.


**Example:**
Imagine a "Sign In" button that logs in and takes you to a dashboard page.
```robotframework
ClickText      Sign In
VerifyText     Welcome to your dashboard
```

*   **Accuracy:** Very high. Usually correct, but can hit duplicates and partial match surprises without scoping or exact mode.  
*   **Resilience:** If the underlying HTML structure changes (e.g., `<div>` becomes `<button>`) but the label "Login" remains, your test still passes.
*   **Maintainability:** Even if the text *does* change (e.g., from "Login" to "Sign In"), updating a single word in your test script is significantly faster and easier than debugging and rewriting complex XPath strings.


!!! note "Controlling Precision" 
    **Partial Matching:** QWeb defaults to substring matching. This means ClickText Save will match a button labeled "Save Changes".
    If partial matching causes issues (e.g., clicking "Save All" when you wanted "Save"), you can enforce exact matches:

    *   **Per Keyword:** `ClickText    Save    partial_match=False`
    *   **Globally:** `SetConfig    PartialMatch    False`


## 2. Item Locators (Attributes)

**Keywords:** `ClickItem`, `VerifyItem`, `HoverItem`

When an element has no visible text (like an icon, a trash can button, or a logo), use **Item** keywords. These keywords look for relevant HTML attributes that describe the element, such as:

*   `title` (Tooltip text)
*   `alt` (Image description)
*   `value` (Input button text)
*   `placeholder` (Input hint text)

**Example:**
Imagine a "Clear Search" button that is just an 'X' icon but has `title="Clear"`.

```robotframework
ClickItem      Clear
```

**Accuracy:** Good when attributes like title, alt, placeholder are unique and stable.  
**Resilience:** More stable than XPath, but attributes may be missing, reused, or changed by developers  
**Maintainability:** Often a small change, but sometimes you must switch strategy if attributes disappear.

!!! tip "Limiting elements using **tag** attribute"
    Narrow your attribute search to specific element types by specifying the tag attribute.
    ```robotframework
    # Matches only elements with tag "custom_input" and attribute value "Reset"
    ClickItem   Reset    tag=custom_input
    ```

    Using the tag attribute can also improve search performance.

## 3. Element Locators (XPath)

**Keywords:** `ClickElement`, `VerifyElement`

For the "tricky 10-20%" of elements that have no text and no descriptive attributes, you can fall back to standard XPaths selectors. This gives you full control but makes your tests more brittle to layout changes.

```robotframework
# Using XPath
ClickElement   xpath\=//div[@class="user-menu"]//button

```

!!! warning "XPath does not work inside Shadow DOM"
    XPath selectors cannot cross Shadow DOM boundaries.

    This is a **browser-level technical limitation**, not a QWeb restriction.  
    All modern browsers isolate Shadow DOM trees from XPath evaluation by design.

    Use QWeb Item selectors or text-based locators when working with [Shadow DOM ](shadow_dom.md) content.


**Accuracy:** Deterministic and precise if the XPath targets the correct element.  
**Resilience:** Easily breaks if the DOM structure changes, wrappers are modified, or the layout is refactored.    
**Maintainability:** Debugging and repairing XPath usually takes longer than changing text or an attribute.

!!! tip "Syntax Note"
    When using XPaths in Robot Framework, you often need to escape the equals sign (`\=`) if it's part of the locator string.

## 4. Image Locators (Bitmap)

**Keywords:** `ClickIcon`, `VerifyIcon`  


As a last resort, QWeb can find elements by comparing a reference image against the screen.

```robotframework
ClickIcon      user_avatar.png
```

**Accuracy:** Depends on matching tolerance, rendering, and capture quality.    
**Resilience:** Image matching is sensitive to resolution, theme changes, and rendering differences. Use this only when absolutely necessary (e.g., verifying a specific logo or chart)  
**Maintainability:** Requires recapturing assets and revalidating across environments.


## Summary: Naming Conventions

QWeb keywords are named consistently to help you choose the right strategy:

| Suffix | Strategy | Example |
| :--- | :--- | :--- |
| **...Text** | Visible UI Text | `ClickText`, `VerifyText` |
| **...Item** | Attributes (Title/Alt) | `ClickItem`, `IsItem` |
| **...Element** | XPath | `ClickElement`, `VerifyElement` |
| **...Icon** | Image / Bitmap | `ClickIcon`, `VerifyIcon` |

