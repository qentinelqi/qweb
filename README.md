<img id="qweb" src="https://github.com/qentinelqi/qweb/raw/master/images/qweb.png" alt="QWeb">

> Keyword based test automation for the web.

---
![License][license-badge]
![Python versions][python-versions-badge]
![Release][pypi-badge]
![Windows Acceptance][win_ci_badge]
![Linux Acceptance][linux_ci_badge]
![MacOS Acceptance][macos_ci_badge]
[![Tested with][pace-badge]][pace-url]
[![Slack][slack-badge]][slack-url]

### Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Windows](#windows)
  - [Linux/Mac](#linuxmac)
- [Usage](#usage)
  - [Keyword documentation](#keyword-documentation)
  - [Examples](#examples)
    - [Basic usage](#basic-usage)
    - [Shadow DOMs and visibility](#shadow-doms-and-visibility)
    - [Timeouts and anchors](#timeouts-and-anchors)
    - [Other locators](#other-locators)
    - [Working with tables](#working-with-tables)
    - [Changing configuration](#changing-configuration)
- [Changelog](#changelog)
- [Contribute](#contribute)
- [Community](#community)
- [License](#license)
- [Resources](#resources)

---

## Introduction

QWeb is an open source web automation interface in [Robot Framework](https://robotframework.org/). It makes automation **rapid, robust, and fun**.

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
Python **3.7-3.10** and Robot Framework 3.2.2 or above. Browser drivers need to be installed separately.

(Note that support on Macs with Apple based silicon (M1) requires MacOS version 12/Monterey or above or [custom installation](https://github.com/qentinelqi/qweb/blob/master/docs/qweb_mac_m1_installation.md).)

## Installation

### Windows
```bash
    pip install QWeb
```

### Linux/Mac
```bash
    python3 -m pip install -U pip
    python3 -m pip install QWeb
```


Running the above command installs also supported Selenium and Robot Framework versions + other dependencies, but you still need to install `browser drivers` separately. Please refer to [Selenium documentation](https://www.selenium.dev/selenium/docs/api/py/index.html#drivers) for more information on how to install browser drivers manually OR use 3rd party packages like [WebDriverManager](https://pypi.org/project/webdrivermanager/).


[Back To The Top](#qweb)

---



## Usage

### Keyword documentation
See list of keywords and their usage on 

* [Keyword documentation](https://qentinelqi.github.io/qweb/QWeb.html)
* [Copado Robotic Testing support pages](https://help.pace.qentinel.com/pacewords-reference/current/pacewords/all.html) 

[Back To The Top](#qweb)

### Examples

#### Basic usage

The preferred way to interact with web elements is using their **text** property. Most elements like input fields and dropdowns can also be found by closest label (text).

```RobotFramework
*** Settings ***
Library    QWeb     # Import library

*** Test Cases ***
Basic interaction
    OpenBrowser         https://qentinelqi.github.io/shop      chrome   # Open chrome and goto given url
    VerifyText          The animal friendly clothing company            # Assert heading text
    ClickText           Scar the Lion                                   # Click link text
    ClickText           Add to cart                                     # Click *button* with specific text
    DropDown            Size            Large                           # Select value (Large) from dropdown (Size)

```
#### Shadow DOMs and visibility
Most common cases when text or element is not found are:
- Element has (incorrectly?) some attribute set so, that it's considered invisible.
- Element is under shadow dom (i.e. has #shadow-root parent element)

QWeb searches for visible elements by default, but can be instructed to work with invisible elements as well. See keyword documentation of **SetConfig** and the following parameters:
- Visibility
- Offsetcheck
- InViewport

Elements under shadow DOM can not be found using xpaths. However, all *Text, *Item and *Input keywords do support extending the search to Shadow DOM elements. We intentionally keep this under separate setting for ensuring compatibility with older test cases. 

Example:
```RobotFramework
*** Settings ***
Library    QWeb     # Import library
SetConfig            ShadowDOM            True  # extends search to shadow dom elements
OpenBrowser          chrome://settings/content/popups   chrome
ClickText            Sites can send pop-ups 
```

#### Timeouts and anchors

By default QWeb tries to locate the element 10 seconds (default time can be configured). Timeout can also be individually given for each keyword as an argument.

When text to be found is not unique, an 'anchor' argument can be given to pinpoint which instance of text we want to interact with. Anchor can be either another text nearby or index.

```RobotFramework
ClickText   Sign-in
ClickText   Sign-in     timeout=30

ClickText   Sign-in     anchor=Email
ClickText   Sign-in     index=3
```

#### Other locators

Non-textual locators can be used with `ClickElement`and `ClickItem`keywords.

```RobotFramework
ClickElement    xpath\=//button[@class="my_class"]   # xpath
ClickItem       Increment quantity                   # alt text

```

#### Working with tables

QWeb includes keywords to interact with table data easily.

Consider the following table as an example:
<img src="https://github.com/qentinelqi/qweb/raw/master/images/example_table.png" alt="Example table">

```RobotFramework
UseTable    Firstname

${row}=     GetTableRow     //last                        # returns 5
${row}=     GetTableRow     //last    skip_header=True    # returns 4
...
${row}=     GetTableRow     Jim                           # returns 4
${row}=     GetTableRow     Jim    skip_header=True       # returns 3

${cell_value}=     GetCellText     r1c2                   # Returns "John", first name is column 2.

${cell_value}=     GetCellText     r-1/c2                 # Returns "Tina", -1 points to last row
${cell_value}=     GetCellText     r-2/c2                 # Returns "Jim", -2 points to second last row
```

#### Changing configuration
QWeb's behavior can be changed with SetConfig keyword.

```RobotFramework

SetConfig     SearchMode     Draw       # Highlight all found elements with blue rectangle

SetConfig     DefaultTimeout    60s     # change default/automatic timeout for all keywords
VerifyText    User account created      # Re-tries to find text "User account created" 60 seconds and then fails, if text is not visible
```
More examples on [QWeb tutorial](https://github.com/qentinelqi/qweb_workshop).

[Back To The Top](#qweb)

---

## Changelog

See [RELEASE.md](https://github.com/qentinelqi/qweb/blob/master/RELEASE.md)

[Back To The Top](#qweb)

## Contribute

Found an bug? Want to propose a new feature or improve documentation? Please start by checking our [contribution guide](https://github.com/qentinelqi/qweb/blob/master/CONTRIBUTING.md)

[Back To The Top](#qweb)

## Community

Want to join the community at Slack? On the official Robot Framework workspace, there is a QWeb channel where you can discuss with others about keywords, issues and improvements. [Join Now](https://robotframework.slack.com/archives/C029L0N3N81)

[Back To The Top](#qweb)

## License

Apache 2.0 License. See [LICENSE](https://github.com/qentinelqi/qweb/blob/master/LICENSE).


[Back To The Top](#qweb)

## Resources
* [QWeb home page](https://qentinel.com/qweb-open-source/)
* [QWeb tutorial](https://github.com/qentinelqi/qweb_workshop)



---
[license-badge]: https://img.shields.io/github/license/qentinelqi/qweb
[linux_ci_badge]: https://github.com/qentinelqi/qweb/actions/workflows/linux_acceptance.yml/badge.svg
[win_ci_badge]: https://github.com/qentinelqi/qweb/actions/workflows/win_acceptance.yml/badge.svg
[macos_ci_badge]: https://github.com/qentinelqi/qweb/actions/workflows/mac_acceptance.yml/badge.svg
[pace-url]: https://robotic.copado.com
[pace-badge]: https://img.shields.io/badge/Tested%20with-Copado%20Robotic%20Testing-blue
[python-versions-badge]: https://img.shields.io/pypi/pyversions/QWeb
[pypi-badge]: https://img.shields.io/pypi/v/QWeb?color=green
[slack-badge]: https://img.shields.io/badge/Slack-QWeb-blue?style=flat-square&logo=Slack
[slack-url]: https://robotframework.slack.com/archives/C029L0N3N81
