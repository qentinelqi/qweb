# Using QWeb from Python

While QWeb is primarily known as a Robot Framework library, it can also be used directly as a Python module. This allows you to leverage QWeb's "Text-First" locators and automatic waiting strategies within standard Python scripts, `pytest` suites, or other automation frameworks.

## Setup

You do not need a separate installation. The standard `pip install QWeb` includes the Python bindings.

## Basic Usage

To use QWeb in Python, import the `QWeb` class and instantiate it. All Robot Framework keywords are available as class methods, converted to standard Python **snake_case**.

*   `ClickText` --> `click_text`
*   `VerifyElement` --> `verify_element`
*   `OpenBrowser` --> `open_browser`

### Example Script

Here is a complete example of a Python script using QWeb:

```python
from QWeb import QWeb

# 1. Initialize the library
qweb = QWeb()

# 2. Open Browser
# Note: Drivers are still handled automatically!
qweb.open_browser("https://qentinelqi.github.io/shop", "chrome")

# 3. Interact using QWeb keywords (in snake_case)
qweb.verify_text("The animal friendly clothing company")
qweb.click_text("Scar the Lion")

# 4. Assertions
# These will raise standard Python exceptions if they fail
qweb.verify_text("Add to cart")

# 5. Get Data
# Keywords that return values work as expected
title = qweb.get_title()
print(f"Page Title is: {title}")

# 6. Teardown
qweb.close_all_browsers()
```

## Why use QWeb with Python?

1.  **Powerful Locators:** You get the benefit of `click_text("Save")` instead of managing complex Selenium XPaths or Page Object Models.
2.  **Auto-Waiting:** You don't need to write explicit `WebDriverWait` loops; QWeb handles retries automatically.
3.  **Tooling:** You can use your favorite Python test runners like `pytest` or `unittest`.

## Limitations

*   **Reporting:** You lose Robot Framework's automatic HTML log and report generation. You will need to rely on your test runner (like `pytest-html`) for reporting.
*   **Listener Support:** Some advanced Robot Framework listener features may not be available.