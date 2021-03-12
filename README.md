<img id="qweb" src="./images/qweb.png" alt="QWeb">

> Keyword based test automation for the web.

---
![License][license-badge]
![Python versions][python-versions-badge]
![Release][pypi-badge]
![Build Status][build-badge]
[![Tested with][pace-badge]][pace-url]

### Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [Keyword documentation](#keyword-documentation)
  - [Examples](#examples)
- [Changelog](#changelog)
- [Contribute](#contribute)
- [License](#license)

---

## Introduction

QWeb is an open source web automation interface in [Robot Framework](https://robotframework.org/). It makes automation **rapid, robust, and fun**.

QWeb aims to make web automation easy and maintainable by:
* providing high level keywords for accessing any web page element
* preferring text locators (UI texts) but supporting also other locator strategies (xpaths, css selectors)
* automatically handling latencies etc. via automatic wait times
* automatically handling unexpected alerts
* minimizing the maintenance effort

See [examples](#examples).

[Back To The Top](#qweb)

---
## Requirements
Python 3.6+ and Robot Framework 3.2.2+. Browser drivers need to be installed separately.

## Installation

### Windows
```bash
    pip install QWeb
```

### Linux/Mac
```bash
    python3 -m pip install QWeb
```

In some environments you might need to upgrade pip first:

```bash
    python3 -m pip install –upgrade pip
```


Running the above command installs also supported Selenium and Robot Framework versions + other dependencies, but you still need to install `browser drivers` separately. Please refer to [Selenium documentation](https://www.selenium.dev/selenium/docs/api/py/index.html#drivers) for more information on how to install browser drivers manually OR use 3rd party packages like [WebDriverManager](https://pypi.org/project/webdrivermanager/).


[Back To The Top](#qweb)

---



## Usage

### Keyword documentation
See list of keywords and their usage on 

* [Keyword documentation](https://qentinelqi.github.io/qweb/QWeb.html)
* [Qentinel support pages](https://help.pace.qentinel.com/pacewords-reference/current/pacewords/all.html) 

[Back To The Top](#qweb)

### Examples

#### Basic usage

The preferred way to interact with web elements is using their **text** property. Most elements like input fields and dropdowns can also be found by closest label (text).

```
*** Settings ***
Library    QWeb     # Import library

*** Test Cases ***
Basic interaction
    OpenBrowser         https://qentinelqi.github.io/shop      chrome   # Open chrome and goto given url
    VerifyText          The animal friendly clothing company    # Assert heading text
    ClickText           Scar the Lion   # Click link text
    ClickText           Add to cart     # Click *button* with specific text
    DropDown            Size            Large  # Select value (Large) from dropdown (Size)

```

#### Timeouts and anchors

```
# TIMEOUTS
# By default QWeb tries to locate the element 10 seconds (time can be configured)
ClickText   Sign-in  # Tries to locate and click text "Sign-in" until 10 seconds has passed or until element is found.

# Timeout can be controlled using argument
# Below example re-tries to find element until it's found or 30 seconds has passed. If element is not found after timeout, test will fail.
ClickText   Sign-in     timeout=30  

# ANCHORS
# When multiple elements with same text are found, 
# QWeb can be guided to interact with specific element
# using anchors and indexes

# clicks "Sign-in" text closest to text "Email"
ClickText   Sign-in     anchor=Email   

# clicks the third "Sign-in" on a page
ClickText   Sign-in     index=3
```

#### Other locators

```
# ClickElement
# xpaths and css selectors are supported. 
# Note that equal sign must be escaped
ClickElement    xpath\=//button[@class="my_class"]

# ClickItem
# ClickItem finds element based on any unique attribute,
# in this particular case ALT texts
ClickItem       Increment quantity

```

#### Working with tables

Consider the following table as an example:
![Example table](https://github.com/qentinelqi/qweb/raw/main/images/example_table.png)

```
# First focus on a table using any text in it (column header etc.)
UseTable    Firstname

# Get row number based on content (or last row)
${row}=     GetTableRow     //last                        # returns 5
${row}=     GetTableRow     //last    skip_header=True    # returns 4
...
${row}=     GetTableRow     Jim                           # returns 4
${row}=     GetTableRow     Jim    skip_header=True       # returns 3

# Get value in specific cell
${cell_value}=     GetCellText     r1c2  # Returns "John", first name is column 2.

# Negative numbers as row number will count from the end of table
${cell_value}=     GetCellText     r-1/c2  # Returns "Tina", -1 points to last row
${cell_value}=     GetCellText     r-2/c2  # Returns "Jim", -2 points to second last row
```

#### Changing configuration

```
# QWeb's behavior can be configured with SetConfig keyword

# Highlight all found elements with blue rectangle
SetConfig     SearchMode     Draw

# Set automatic timeout time
SetConfig     DefaultTimeout    60s     # change default/automatic timeout for all keywords
VerifyText    User account created   # Re-tries to find text "User account created" 60 seconds and then fails, if text is not visible
```


[Back To The Top](#qweb)

---

## Changelog

See [RELEASE.md](./RELEASE.md)

[Back To The Top](#qweb)

## Contribute

Found an bug? Want to propose a new feature or improve documentation? Please start by checking our [contribution guide](./CONTRIBUTING.md)

[Back To The Top](#qweb)

## License

Apache 2.0 License. See [LICENSE](./LICENSE).


[Back To The Top](#qweb)

## More info
* [Qentinel.com: QWeb intro](https://qentinel.com/qweb-open-source/)
* [QWeb Workshop/tutorial repository](https://github.com/qentinelqi/qweb_workshop)



---
[license-badge]: https://img.shields.io/github/license/qentinelqi/qweb
[build-badge]: https://pace.qentinel.com/masters/master-ox36ary2sa/buildStatus/icon?job=QWeb_GitHub%2Fmaster
[pace-url]: https://pace.qentinel.com
[pace-badge]: https://img.shields.io/badge/Tested%20with-Qentinel%20Pace-blue
[python-versions-badge]: https://img.shields.io/pypi/pyversions/QWeb
[pypi-badge]: https://img.shields.io/pypi/v/QWeb?color=green