# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Updated documentation of **GetPDFText** and **GetFileText**
- Changed **IsModalXpath** to enforce timeouts


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