# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Suppress "Choose search engine" dialog in Chrome
- Bumped scikit-image to a version supporting Python 3.12
- Bumped pynput to version 1.7.7

## [3.3.3] - 2024-06-28

### Fixed
- Fixes regression in v3.3.2 which caused *Checkbox keywords to fail if checkbox element is not fully loaded and visible

## [3.3.2] - 2024-06-20

### Fixed
- Added support for non-breakable spaces when searching for text directly inside `<slot>`
- partial_match=False was not correctly handled as boolean in few places
- partial_match was not taken into account at all on ClickCheckbox even if it should have
- Improved **table** keywords documentation regarding the coordinate format

### Changed
- Made **//last** argument in GetTableRow case insensitive
- Deps: Made numpy a direct dependency and locked version since opencv does not yet have a release with numpy 2.0 support
- Deps: Bumped minimum allowed version of requests due to security alert
- Deps: Allows more recent versions of pyobjc on Mac

## [3.3.1] - 2024-05-22

### Added
- Added support for clicking elements by **ClickText** on the uncommon situation where text is directly on `<slot>` tag and not it's parent or child. By default slots without clickable parent/child are otherwise considered invsible by our visibility check as they have not offsets etc.

### Changed
- Changed tests & duty file to support both parallel and serial execution locally and with or without http server.
- Changed Chrome shadow dom case so that it will work with Chrome 125 and lower versions.

## [3.3.0] - 2024-05-15

### Added
- Added support for treating color differences as meaningful in *Icon keywords (with **grayscale** argument).
- *Icon keywords support new argument **tolerance**
- Browser version management with **browser_version** added to Firefox and Edge in addition to previously existing Chrome.
  - Note that with Edge on Windows local admin rights are needed for install to succeed
- Option to remove newlines from returned value added to GetInputValue (by argument **remove_newlines) 

### Fixed
- VerifyTable to not break on "special characters" like "[", "]", "*" or "?" 
- fix: UploadFile to find inputs of type file when searching with xpath locator
- GetPdfText and GetFileText documentation fixed to match how they actually work
- Fixed examples in VerifyAll docs

### Changed
- Refactor: changed version check from deprecated pkg_resources to importlib.metadata
- Pipeline: tests are run in parallel with Pabot
- Pipeline: Test files are served using http server instead of opening static files
- Ruff taken into use as one of pipeline checks / duty
- Removed deprecated methods from unit tests
- CONTRIBUTING.md updated


## [3.2.1] - 2024-04-08

### Fixed

- RunBlock fails with uninformative error message
- GetCellText and GetText not able to get text directly under `<slot>`
- #141 
  -   Anchor coordinates were in some cases taken from parent, not from the element actually containing anchor text
- New typing issue in selenium 4.19
- Bumped Pillow to a version having latest security fixes

## [3.2.0] - 2024-03-11

### Added
- Adds "strict mode" to SetConfig [SearchDirection](https://qentinelqi.github.io/qweb/QWeb.html#searchdirection)
- Adds "delay" kwarg support to WriteText
- Adds "partial_match" support to VerifyTable and Click Cell

### Fixed
- QWeb tries to inject JQuery to web pages #139
- Let user decide if cookies are logged or not #138
- Clean up unit tests and acceptance tests #90 
- Table keywords gave unhelpful error if UseTable was not used
- Many keyword doc fixes

## [3.1.0] - 2024-01-26

### Added
- Support for **Robot Framework 7**
- New keywords for handling table column headers:
  - **GetColHeaderCount** (Gets the amount of columns)
  - **GetColHeader** (Gets all column headers as list or specific column header based on index)
  - **VerifyColHeader** (Verifies that column headers includes specific text, optionally in specific position) 

### Fixed
-  Handling of booleans given in string format in OpenBrowser prefs (i.e… "True")

### Changed
- Updated workflow actions to newer version
- Bumped lowest allowed Pillow version (security fixes)

## [3.0.1] - 2023-12-21

### Fixed
- Browserstack desktop browser names changed to be case insensitive

### Removed
- Argument "reuse_service" removed from Safari as it was removed in selenium 4.16

### Changed
- Pylint version bumped
- SwitchBrowser will try to focus on previously focused tab in order to bring window to foreground.
  - Success depends on os/window manager 
- Refactored QWeb/config as functions there were masked by keywords/config.
  - This will make it easier to use set_wait_function to override default wait function

## [3.0.0] - 2023-10-20

### Added
- OpenBrowser keyword to support Selenium 4.10 and above
  - Service class taken into use
  - Support for automatic driver/browser management via Selenium Manager (if drivers are not in PATH)
  - Chrome: Support for specific **browser_version** (downloads Chrome for Testing if needed)
- BrowserStack/mobile integration to support OS Version
- Added "Introduction" section to keyword documentation
  
### Changed
- OpenBrowser kw documentation updated/more examples added, including BrowserStack usage and local android device usage.
- DragDrop to support also elements that do not have "draggable" attribute set
- Re-used variable "url" renamed in VerifyLinks
- Security: bumped opencv and Pillow versions
- Updated readme.md
  
### Fixed
- `SetConfig HandleAlerts False` was not raising exceptions
- SetConfig argument types modified in order to avoid automatic type conversion
  - This fixes issue of using robot fw format (variable containing list) in `SetConfig RunBefore`

### Removed
- IE Support
- Robot Framework 3.2.2 support (4.1.3 is the new minimum)
- Python 3.7 support as it has been [already EOL'd](https://devguide.python.org/versions/) and some security fixes for dependencies are not released for Python 3.7


## [2.2.3] - 2023-09-18
### Fixed
- Regression: VerifyCheckboxValue not finding checkbox by label in specific views
- Improved attribute search in specific Salesforce views
### Added
- Examples of using proxies, profiles and portable binary to OpenBrowser kw doc

### Changed
- Changed deprecated license_file parameter in setup.cfg

## [2.2.2] - 2023-09-06

### Added
- Enable using QWeb directly from Python
### Fixed
- ClickCell not clicking a sub-element when tag used
- VerifyFile keyword not working correctly when ${BASE_IMAGE_PATH} variable is used

### Changed
- IsText default timeout increaded to 0.5
- ScrollTo keyword to support anchor
- Bumped opencv, selenium, Pillow, scikit-image, and requests dependency version. 

## [2.2.1] - 2023-08-02

### Fixed
- Handled situation where Chrome v115 gives a new exception
- Minor fix to improve finding input via label under shadow dom
  
## [2.2.0] - 2023-06-14

### Added
- New keyword [Scroll](https://qentinelqi.github.io/qweb/QWeb.html#Scroll) for scrolling with keys (PageDown etc.) in cases where other scrolling means do not work reliably.

### Changed

- Updated pyobjc-core and pyobjc for Mac. This should enable direct installation with Python 3.11 on Mac.
- Locked PyScreeze dependency version, as the latest one has a slight issue with Mac.
- Bumped versions of testing dependencies.
- Added Edge to Linux pipeline
- Modified over aggressive "No Browser Open" error message. One should get more meaningful messages in other fatal cases, for example when webdriver / browser is not installed at all.


## [2.1.2] - 2023-03-24

### Added
- New InputHandler javascript for cases where send_keys does not work reliably (e.g. iPad)

### Changed
- CaptureIcon returns saved file's path in order to work same way as LogScreenshot
- Minor documentation fixes

## [2.1.1] - 2023-03-08

### Added
- Updated dependencies to support Python 3.11
### Fixed
- Fixed regression where in special cases normal elements where not found correctly when Shadow DOM setting was on


## [2.1.0] - 2023-02-06

### Added
- Mobile emulation support to Open Browser

### Fixed
- Improved Shadow DOM support for:
  - frames
  - clickable elements
  - elements having non-breaking spaces in text
- Minor fixes to keyword documentation

## [2.0.7] - 2022-12-14
### Added
- Update wheel to enable usage of Robot Framework 6.x

### Fixed
- Filter by modal dialog was not working with inputs, if found with css search
- Improved ability to find dropdowns under shadow DOM

### Changed
- Minor updates to CI pipeline
- Moved unnecessary log messages to debug logging level

## [2.0.6] - 2022-11-23
### Added
- Added support for global hotkeys in PressKey keyword
- Added offset arguments for locator element in DragDrop keyword
- Added Shadow DOM support for DropDown keyword
  
### Changed
- Deprecation warning added to OpenBrowser when using IE
- Updated Selenium to 4.6.0 and improved typing
- Updated Pillow to 9.3.0
- Minor change how ClickCheckbox works to better support Salesforce checkboxes
- Suppressed some unnecessary warnings from webdriver (moved to DEBUG log level)


## [2.0.5] - 2022-10-20
### Added
- Exclude Robot Framwork 6.x in requirements for now
  
### Fixed
- Filtering out unnecessary tags (script etc.) in shadow dom text search
- Fix for using attribute value as a locator in safari
  - This was failing in iOS Safari if found element had no attributes


## [2.0.4] - 2022-09-22
### Added
- Added support for index argument when using xpath
- Added support for verifying text including single, double and mixed quotes
- Added support for typing to textareas under shadow dom using attribute
  
### Fixed
- Fixed handling of line breaks when check=True (TypeText)

## [2.0.3] - 2022-08-08
### Added
- Added shadow dom support for GetText with attribute value & tag
- Added tests for VerifyElement keyword
  
### Changed
- Changed handling of (command line) arguments for Firefox
  - version 103 and above handle incorrect arguments differently than previous versions
- Bumped DebugLibrary version for RF 5.x support
- Changed generated screenshot file name handling
  - Generated screenshot file names should not be longer than accepted by OS

## [2.0.2] - 2022-06-09
### Fixed
- Fixed regression (unexpected timeouts on default settings) caused by latest (v15.5) Safari & Safaridriver
- Fixed error on ClickItem when SearchMode is set to "None"
- Fixed highlighting found element on VerifyElementText

### Changed
- Added typing and type checking (mypy) to pipeline
- Changed BrowserStack capabilities to conform with new format + accept additional capabilities
- Improved local development tasks (duties) to support running acceptance tests on different platforms
- Removed unnecessary logging from timeout decorator
- Improved pipeline to re-run failed cases automatically

## [2.0.1] - 2022-04-25
### Fixed
- Enhanced Safari support: Multiple fixes to Safari regarding handling frames and windows
  
### Added
- Added robot framework 5.0 support
- LogScreenshot: Support for full page screenshots
- Added support for different operators (equal/not equal/greater than/less than/contains) to VerifyAttribute
- Added Safari specific solution for COMMAND key
  
### Changed
- GetWebelement, GetAttribute and VerifyAttribute now accept css selectors with element_type=css
- Updated Pillow dependency to latest version
- Added Safari to GitHub pipeline
- Added documentation for PartialMatch configuration


## [2.0.0] - 2022-03-24
### Changed
- Moved to Selenium 4
- Removed support for Python 3.6
- Added support for Python 3.10
- Updated dependencies
- Enhanced support for M1 Macs
- Added support for extending element searches to shadow dom
  - This can be enabled using `SetConfig    ShadowDOM   True` 
  - All *Text, *Item and *Input keywords are supported
  - Note: *Element keywords are not supported, as xpaths do not work with shadow doms.
- Added summary table to **SetConfig** documentation to make it easier to understand which kind of configurations are possible
- Added ability to change element hightlight color when needed. Example `SetConfig   HighlightColor    orange`  

## [2.0.0rc1] - 2022-03-10
### Changed
- Moved to Selenium 4
- Removed support for Python 3.6
- Added support for Python 3.10
- Updated dependencies
- Enhanced support for M1 Macs
- Added support for extending element searches to shadow dom
  - This can be enabled using `SetConfig    ShadowDOM   True` 
  - All *Text, *Item and *Input keywords are supported
  - Note: *Element keywords are not supported, as xpaths do not work with shadow doms.
- Added summary table to **SetConfig** documentation to make it easier to understand which kind of configurations are possible
- Added ability to change element hightlight color when needed. Example `SetConfig   HighlightColor    orange`  

## [1.2.5] - 2022-02-02
### Fixed
- Fixed issue #53
### Changed
- Bumped **Pillow** to verson **9.0.0**
- Clarified SetConfig/SearchDirection docs

## [1.2.4] - 2022-01-10
### Fixed
- Fixed rare issue of getting  ``AttributeError: 'NoneType' object has no attribute 'get'`` on Firefox

## [1.2.3] - 2021-11-25
### Added
- New community home page added (https://www.qweblibrary.org/)
- Added test requirements file (requirements_test.txt)
### Changed
- Updated documentation of **GetPDFText** and **GetFileText**
- Changed **IsModalXpath** to enforce timeouts

### Fixed
- Fixed  ``SetConfig   CaseInsensitive``

## [1.2.2] - 2021-11-03
### Changed
- Selenium locked to version 3.141.0
- opencv-python locked to version 4.5.3.56
- Documentation updates

## [1.2.1] - 2021-10-20
### Added
- Configuration option **IsModalXpath** to limit text based search to elements under specific (modal) element
- Keywords **IsItem** and **IsNoItem**
- Added excludeSwitches option to Edge & Chrome, should not log all sorts of unnecessary things to console
- Added --no-sandbox option when Edge is run in docker

### Fixed
- **LogPage** keyword
- Fixed: example in ClickText documentation does not display correctly

### Changed
- Security update to OpenCV dependency
- Imported functions that are not keywords removed from documentation
- Clarified ExcpectFileDownload documenation


## [1.2.0] - 2021-09-30
### Added
- Support for Edge in Linux & Mac
- Support for Retina displays to Icon* keywords
- Tags to keyword documentation
- SwitchBrowser keyword
- Forward keyword
- Description how to get QWeb working on Apple M1 silicon
- Edge added as testing target to pipeline
  
### Fixed
- Icon keywords should be (less) resolution dependent. Scaling to different resolutions improved
- Import error in Ubuntu if tkinter dependencies are not fulfilled now produces visible instructions
- "\" characters not escapted correctly in keyword documentation

### Changed
- Security update to Pillow dependency
- Minor change on dropdown search order as Firefox was behaving differently than other browsers

## [1.1.0] - 2021-09-01
### Fixed
- Fixed rare timeout issue when reload happens while searching for frames. This happened from time to time especially with Firefox.

### Changed
- TypeText, HoverElement, ClickElement and VerifyInputValue now optionally take a WebElement instance as a locator.
- Added deprecation warning to **ScanClick** and **SkimClick**
- Added "click" argument description to TypeText docstring
- Multiselection dropdown support with adding argument "unselect=True" to **DropDown**
- Multiselection support to **GetSelected** too. If there are multiple options selected, each selection will be separated by comma (,)
- Added argument **header_only** to **VerifyLinks**. Even if header and get normally return the same status, server can be configured to return different code from header.
- **RunBefore** made public and modified to accept Robot Framework syntax
- Added **Related Keywords** section to documentation for most keywords

## [1.0.6] - 2021-07-02
### Changed
- Fixed TypeSecret not working on debugger under RFW 4.x
- Changed SearchMode default value to "Draw". Blue rectangle is now by default drawn over found elements

## [1.0.5] - 2021-06-16
### Added
- Acceptance tests for multiple clickable elements in a cell
- Added keywords GetAttribute and VerifyAttribute

### Changed
- Updates for ClickCell keyword: checks for index value and more descriptive documentation
- Fixed DoubleClick argument usage consistency between keywords
- Fixed "ClearKey" not being reset when using ResetConfig
- Fixed ClickIcon not overriding image on newer linux/scrot versions
- Fixed VerifyTextCount not failing when text is not found at all

## [1.0.4] - 2021-05-24
### Added
- Added argument 'anchor_type'. This can be set to 'text' if all numeric values in anchors should be handled as textual anchors and not as indices.
- Added keywords GetUrl and VerifyUrl
- Added keywords GetTitle and VerifyTitle
- Added keyword Back

### Changed
- Fixed / changed how profiles are handled with Firefox


## [1.0.3] - 2021-05-3
### Added
- Robot FW 4.x support and pipeline
- Added Robot FW 4.x support to setup.py
- Added duty file for local development tasks
- Added 'pylint' back to pipeline

### Changed
- Fixed issue #6: added argument 'normalize' to verifypdftext/verifyfiletext
- Fixed copyright message on unit tests
- Updated keyword documentation to new RFW 4.x format

## [1.0.2] - 2021-03-24
### Added
- Python 3.9 support

### Changed
- Bumped Pillow version
- Bumped scipy version
- Added own scikit-image versions for Python==3.6 and > 3.6
- Modified screenshots.py based on scikit-image api changes
- Moved CI pipeline to GitHub

## [1.0.1] - 2021-03-11
### Changed
- Bumped versions for pillow, scikit-image and opencv-python dependencies
- Changed default BrowserStack Chrome version identifier to 'latest'

### Added
- Added keyword documentation to ./docs/QWeb.html

## [1.0.0] - 2021-03-09
### Changed
- Moved from private repo to public GitHub

### Added
- First public Pypi release