# Extending QWeb

While QWeb works directly with most web elements out of the box, there may be custom functionalities that make things harder than they should be. Common examples include deeply structured tables or custom dropdown lists that do not use standard HTML tags.

You can extend QWeb's capabilities in two main ways:

1. Creating User Defined Keywords using Robot Framework syntax [1].
2. Creating your own keywords using Python [2].

## 1. Creating Custom Robot Framework Keywords

Custom keywords are typically defined in a resource file. The suggested best practice is to store them in a `resources` folder within your project.

### Structure of a Resource File
It is common to import QWeb and define variables directly in your resource file.

```robotframework
*** Settings ***
Library    QWeb

*** Variables ***
${login_url}    https://login.example.com/

*** Keywords ***
# Define your custom keywords here
```

### Anatomy of a Custom Keyword
A well-designed custom keyword should have a unique, short, and descriptive name. Capitalization and underscores in keyword names do not matter in Robot Framework (e.g., `MyNewKeyword` is the same as `my_new_keyword`).

Every custom keyword should include:

*   A `[Documentation]` tag to explain what it does (crucial for long-term maintenance).
*   Optional `[Arguments]` to pass data in.
*   Optional `RETURN` values to pass data out.

### Re-Using QWeb Keywords
You can define high-level business flows as custom keywords by combining multiple atomic keywords from the QWeb library. For example, you can create a single `Login` keyword to handle repetitive authentication steps:

```robotframework
*** Keywords ***
Login
    [Documentation]    Logs into example.com with known test credentials
    [Arguments]        ${username}    ${password}
    
    GoTo          ${login_url}
    VerifyText    Log In
    TypeText      Username    ${username}
    TypeSecret    Password    ${password}
    ClickText     Log In
    VerifyNoText  Password
```

### Using Javascript
You can also create custom keywords that execute JavaScript directly in the browser using QWeb's `ExecuteJavascript` keyword. 

```robotframework
*** Keywords ***
ScrollToTop
    [Documentation]    Scrolls to the top of the current page
    ExecuteJavascript  window.scrollTo(0,0)
```

### Returning Values
If your keyword extracts data, you can return it to your test case using `RETURN`.

```robotframework
*** Keywords ***
GetTitle
    [Documentation]    Returns the web page's title
    ExecuteJavascript  return document.title;  $TITLE
    RETURN             ${TITLE}
```

!!! warning "Maintenance"
    Try to keep the amount of custom keywords low. Every new custom keyword requires maintenance work in the long run.

---

## 2. Python Keywords

It is advisable to create custom keywords in Python if you need to handle complex logic. Python is much more flexible and allows you to utilize functions from Selenium directly alongside QWeb.

### Anatomy of a Python Keyword
Python source files should be stored in a `libraries` or `libs` folder. By default, all methods defined in a Python class will be exposed as Robot Framework keywords.

1. Create a file named `my_custom_library.py`.
2. Import it in your test suite using `Library  ../libraries/my_custom_library.py`.

### Extending QWeb with Your Own Keywords
The simplest and recommended way to extend QWeb is to retrieve the active QWeb library instance and use it directly.

This approach:

* Uses QWeb’s public API (not internal modules)
* Keeps your extension stable across QWeb updates
* Makes all QWeb keywords and helper methods available
* Reuses QWeb’s built-in waiting, logging, configuration, and error handling

```python
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

class MyCustomLibrary:

    def __init__(self):
        try:
            self.qweb = BuiltIn().get_library_instance("QWeb")
        except Exception:
            raise RuntimeError(
                "QWeb must be imported before using MyCustomLibrary."
            )

    def log_page_title(self):
        """Prints page title to result log."""
        driver = self.qweb.return_browser()

        logger.info(
            f"The title for page '{driver.current_url}' was '{driver.title}'"
        )

```

### Finding Elements using QWeb's Search Functions
If you want to use QWeb's powerful "text-first" locators inside your Python scripts, 
the `get_webelement()` method does the searching for you, handling text, XPaths, and specific element types.

```python
from robot.libraries.BuiltIn import BuiltIn

class MyCustomLibrary:

    def __init__(self):
        try:
            self.qweb = BuiltIn().get_library_instance("QWeb")
        except Exception:
            raise RuntimeError(
                "QWeb must be imported before using MyCustomLibrary."
            )

    def select_custom_dropdown_option(self, label, option):
        """Clicks a custom dropdown and selects an option."""

        # 1. Find the dropdown label using QWeb and click it
        element = self.qweb.get_webelement(label, element_type="text")
        element.click()

        # 2. Use QWeb's text-first click for the option
        self.qweb.click_text(option)

```

!!! info "This is just an example"
    It’s not advisable to use **get_webelement** for this as you could just directly use **click_element/click_text** instead; they will also do the searching for you.