# Anchors & Spatial Search

One common challenge with "Text-First" automation is **Duplicate Text**.
If your page has ten "Edit" buttons, how does QWeb know which one to click?

By default, QWeb interacts with the **first** instance it finds (reading from top-left). To target specific elements, you use **Anchors**.

## 1. Text Anchors

You can identify an element by its proximity to another unique piece of text.

**Scenario:** A login form where the "Sign In" button is right next to a "Cancel" button.

```robotframework
# Clicks the "Sign In" button that is closest to "Cancel"
ClickText    Sign In    anchor=Cancel
```

## 2. Numeric Anchors (Index)

If there is no unique text nearby, you can use a numeric index.

**Scenario:** A list of three "Delete" icons.

```robotframework
# Clicks the 3rd "Delete" text/icon found on the page
ClickText    Delete    anchor=3
```

## 3. Directional Search (`SearchDirection`)

Sometimes, "closest" isn't specific enough. You might need to find an input field that is specifically **below** or **to the right** of a label.

You can control this globally or temporarily using `SetConfig`.

### Modes
*   `closest` (Default): Scans in all directions expanding outwards.
*   `right`: Good for forms (Label -> Input).
*   `left`: Good for checkbox labels (Checkbox <- Label).
*   `up` / `down`: Good for stacked layouts.

### Example: Complex Form
Imagine a form where labels are above the input fields.

```robotframework
# Tell QWeb to look BELOW the anchor text
SetConfig    SearchDirection    down

# This finds the input field under "Email Address"
TypeText     Email Address      demo@example.com

# Reset to default when done
SetConfig    SearchDirection    closest
```

!!! tip "Form Handling"
    For standard forms (Label followed by Input), you typically do **not** need `SearchDirection`. QWeb's default `closest` algorithm is optimized to find input fields associated with labels automatically.
    
    Only use `SearchDirection` if QWeb is picking the wrong element (e.g., an input field from the previous row).
