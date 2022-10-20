# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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