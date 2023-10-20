# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 -            Qentinel Group.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------
from __future__ import annotations
from typing import Union, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

import os
import pkg_resources
import requests
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from QWeb.keywords import window
from QWeb.internal import browser, xhr, exceptions, util
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.browser import chrome, firefox, android, bs_mobile, \
                                  bs_desktop, safari, edge
from QWeb.internal.exceptions import QWebDriverError


@keyword(tags=("Browser", "Getters"))
def return_browser() -> WebDriver:
    r"""Return browser instance.

    Use this function if you need to expand QWeb and require direct browser access.

    Examples
    --------
     .. code-block:: robotframework

        ReturnBrowser


    Related keywords
    ----------------
    \`GetWebElement\`
    """
    return browser.get_current_browser()


@keyword(tags=("Browser", "Interaction"))
def open_browser(url: str, browser_alias: str, options: Optional[str] = None, **kwargs):
    # pylint: disable=line-too-long
    r"""Open new browser to given url.

    Browser options can also be given in the robot command, for example:
    robot -v browser_options:"--kiosk, --disable-gpu" testytest.robot

    Examples
    --------
    .. code-block:: robotframework

        # Basic usage
        OpenBrowser    http://google.com     chrome
        OpenBrowser    file://resources/window.html    firefox

        # Multiple options
        OpenBrowser    http://google.com     chrome    --allow-running-insecure-content, --xyz
        OpenBrowser    http://google.com     firefox   -headless, -private, -xyz
        OpenBrowser    http://google.com     edge      -headless, -inprivate, -xyz

        # Multiple preferences
        OpenBrowser    http://google.com     chrome    prefs="opt1":"True", "opt2":"False"
        OpenBrowser    http://google.com     firefox   prefs="option1":"value1", "option2":"value2"

        # Supply preferences from a dictionary
        ${prefs_d}=    Create Dictionary     option1    value1    option2    value2
        OpenBrowser    http://google.com     firefox    prefs=${prefs_d}

        # Common examples:
        # ----------------

        # Use existing profile
        OpenBrowser    http://google.com     firefox   -profile /path/to/profile
        OpenBrowser    http://google.com     chrome
        ...            --user-data-dir\=C:\\temp,--profile-directory\=Test2
        OpenBrowser    http://google.com     firefox   -private    prefs="option1":"value1"

        # Use portable browser / non-standard installation path / specific driver
        OpenBrowser    about:support    firefox
        ...            binary=C:/Users/SomeUser/temp/FirefoxPortable/App/Firefox64/firefox.exe
        # Use Chromium instead of Chrome:
        OpenBrowser    http://google.com     chrome    chrome_path=/path/to/chromium/chrome.exe
        OpenBrowser    http://google.com     chrome    executable_path=/path/to/my/chromedriver.exe

        # Use proxy
        OpenBrowser    http://google.com    chrome    --proxy_server\=http://127.0.0.1:8080
        OpenBrowser    http://google.com    firefox
        ...            prefs="network.proxy.type":"1","network.proxy.http":"localhost","network.proxy.http_port":"8080"

        # Make Chrome download pdf files instead of opening them
        Open Browser    about:blank         chrome
        ...prefs=download.prompt_for_download: False, plugins.always_open_pdf_externally: True

        # Disable "Save Address" and "Save Credit Card details" dialogs on Chrome.
        OpenBrowser    about:blank           chrome
        ...            prefs="autofill.profile_enabled":false, "autofill.credit_card_enabled":false

        # Mobile emulation
        OpenBrowser    http://google.com     chrome    emulation=iPhone SE
        OpenBrowser    http://google.com     chrome    emulation=375x812

    Selenium Manager
    ----------------

    If browser driver(s) can be found in path, they will be used. If not, Selenium
    Manager tries to download and install them. With Chrome also specific version of
    browser ("Chrome for Testing") can be used.

    **NOTE**: if you are using QWeb in some cloud service,
    it's best to use their method of setting browser version.

    .. code-block:: robotframework

        # If Chrome 117 is already installed, it will be used.
        # If not, Chrome for Testing v117 will be downloaded and used.
        OpenBrowser   https://www.google.com    chrome    browser_version=117

    BrowserStack usage
    ------------------
    QWeb can be directly used with BrowserStack for desktop and mobile browser
    testing. Your own Browserstack credentials are required.

    .. code-block:: robotframework

        # Using BrowserStack for DESKTOP browser testing

        # Note that these variables can be given in run command
        ${PROVIDER}=    Set Variable      bs
        ${USERNAME}=    Set Variable      your_browserstack_username
        ${APIKEY}=      Set Variable      your_browserstack_token
        ${PROJECTNAME}=    Set Variable   qweb_run
        ${RUNID}=       Set Variable      qweb_run
        ${BSOS}=        Set Variable      windows  # optional, default is windows
        OpenBrowser     https://www.google.com    chrome

        ${BSOS}=        Set Variable      osx
        OpenBrowser     https://www.google.com    safari

        # Different os version, browser version and resolution
        ${BSOSVERSION}=    Set Variable      Monterey
        ${BROWSERVERSION}=    Set Variable      15
        ${BSRESOLUTION}=   Set Variable   2560x1440
        OpenBrowser        https://www.google.com    safari


        # Using BrowserStack for MOBILE browser testing
        ${PROVIDER}=    Set Variable      bs
        ${USERNAME}=    Set Variable      your_browserstack_username
        ${APIKEY}=      Set Variable      your_browserstack_token
        ${DEVICE}=      Set Variable      Google Pixel 4
        ${PROJECTNAME}=    Set Variable   qweb_run
        ${RUNID}=       Set Variable      qweb_run_id
        OpenBrowser          https://www.google.com    safari

        # Change to Android device and use specific Android version
        ${DEVICE}=      Set Variable      Google Pixel 4
        ${BSOSVERSION}=    Set Variable      11  # optional
        OpenBrowser     https://www.google.com    chrome


    Mobile emulation
    ----------------
    Giving a valid device profile or screen dimensions in "emulation" argument turns on
    "mobile emulation".

    Supported browsers: desktop Chrome and Edge only.

    See examples above. Always make sure the device profile name exists. You can either define
    a new one or use one of the default profiles:

        * iPhone SE
        * iPhone XR
        * iPhone 12 Pro
        * Pixel 5
        * Samsung Galaxy S8+
        * Samsung Galaxy S20 Ultra
        * iPad Air
        * iPad Mini
        * Surface Pro 7
        * Surface Duo
        * Galaxy Fold
        * Samsung Glazy A51/71
        * Nest Hub
        * Nest Hub Max

    Note that profile names given above are expected to change in new browser releases.
    Always check that the name you are using still exists.

    Local Android device usage
    --------------------------
    QWeb can be used with local Android device with Chrome. Note that this requires
    Android SDK and Appium to be installed in local machine, developer options enabled
    in mobile and USB debugging enabled.

    NOTE: that this feature is not officially supported nor tested in every release. We
    can't guarantee that it will work with every future release and we can't offer support for Android
    side setup.

    Once you have installed Android SDK, starter Appium server and have your local
    Android device plugged in with USB cable, you can run QWeb against local Chrome
    with the following command:

    .. code-block:: robotframework

        OpenBrowser    about:support    android


    To check if your device is correctly connected, run:
    `adb devices` on your terminal and verify that your device is listed.

    Experimental feature for test debugging (for Chrome only):
    ----------------------------------------------------------

    To re-use existing Chrome browser session, you need to set variable BROWSER_REUSE_SESSION
    to True. Next you need to run the first test suite normally including `OpenBrowser` AND
    excluding `CloseBrowser` (e.g. in Tear Down section). The first run will result to
    arguments file in defined output directory. The file name is by default `browser_session.arg`.

    For the next runs, which re-use the existing browser session, you need to specify the argument
    file in robot command-line using `--argumentfile` parameter. Additionally, test
    suites (or debugger) has to run `OpenBrowser` normally. QWeb will automatically override
    normal parameters and use argument file's values instead, thus re-using the existing browser.

    In the first test suite open Chrome browser normally without closing it at the tear down:

    .. code-block:: robotframework

        Set Global Variable   ${BROWSER_REUSE_ENABLED}   True
        OpenBrowser           http://google.com    chrome

    By running above, an argument file `browser_session.arg` is created to the output
    directory or current working directory. To re-use the existing browser session, use
    following command line examples:

    .. code-block:: text

        robot --argumentfile <path>/browser_session.arg ... example.robot
        rfdebug --argumentfile <path>/browser_session.arg

    Parameters
    ----------
    url : str
        URL of the website that will be opened.
    browser_alias : str
        Browser name. For example chrome, firefox or ie.
    options
        Arguments for initialization of WebDriver objects(chrome).
        Some available opts: https://peter.sh/experiments/chromium-command-line-switches/
    kwargs
        prefs=args:
            Experimental options for chrome browser.
        emulation:
            Turns on "mobile emulation" in desktop browser. Useful for testing websites
            simulating a mobile device screen dimensions.
            Supported browsers: desktop Chrome and Edge only.
            Existing device profile name (i.e. "iPhone SE", must exist)
            OR device dimensions in format:
            WIDTHxHEIGHT (i.e. 385x812)

    Raises
    ------
    ValueError
        Unknown browser type

    Related keywords
    ----------------
    \`Back\`, \`CloseAllBrowsers\`, \`CloseBrowser\`, \`GetTitle\`,
    \`GetUrl\`, \`GoTo\`, \`RefreshPage\`, \`ReturnBrowser\`,
    \`SwitchWindow\`, \`VerifyTitle\`, \`VerifyUrl\`
    """
    try:
        logger.info('\nQWeb version number: {}'.format(
            pkg_resources.get_distribution('QWeb').version),
                    also_console=True)
    except pkg_resources.DistributionNotFound:
        logger.info('Could not find QWeb version number.')
    number_of_open_sessions = _sessions_open()
    if number_of_open_sessions > 0:
        logger.warn('You have {} browser sessions already open'.format(number_of_open_sessions))
    option_list = util.option_handler(options)
    b_lower = browser_alias.lower()

    if os.getenv('QWEB_HEADLESS'):
        kwargs = dict(headless=True)
    if os.getenv('CHROME_ARGS') is not None:
        if option_list is None:
            option_list = os.getenv('CHROME_ARGS').split(',')
        else:
            option_list = option_list + os.getenv('CHROME_ARGS', '').split(',')
    logger.debug('Options: {}'.format(option_list))

    bs_project_name = util.get_rfw_variable_value('${PROJECTNAME}') or ""
    bs_run_id = util.get_rfw_variable_value('${RUNID}') or ""
    provider = util.get_rfw_variable_value('${PROVIDER}')

    if provider in ('bs', 'browserstack'):
        bs_device = util.get_rfw_variable_value('${DEVICE}')
        if not bs_device and b_lower in bs_desktop.NAMES:
            driver = bs_desktop.open_browser(b_lower, bs_project_name, bs_run_id, **kwargs)
        elif bs_device:
            driver = bs_mobile.open_browser(bs_device, bs_project_name, bs_run_id, **kwargs)
        else:
            raise exceptions.QWebException('Unknown browserstack browser {}'.format(browser_alias))
    else:
        driver = _browser_checker(b_lower, option_list, **kwargs)
    util.initial_logging(driver.capabilities)

    # If user wants to re-use Chrome browser then he/she has to give
    # variable BROWSER_REUSE=True. In that case no URL loaded needed as
    # user wants to continue with the existing browser session
    is_browser_reused = util.par2bool(util.get_rfw_variable_value('${BROWSER_REUSE}')) or False
    if not (is_browser_reused and b_lower == 'chrome'):
        driver.get(url)
    xhr.setup_xhr_monitor()


@keyword(tags=("Browser", "Interaction"))
def switch_browser(index: Union[int, str]) -> None:
    r"""Switches to another browser instance in browser cache.


    Examples
    --------
     .. code-block:: robotframework

        OpenBrowser     about:chrome                chrome
        OpenBrowser     https://www.github.com      firefox
        OpenBrowser     https://www.google.com      edge
        SwitchBrowser   1       # following keywords will interact with chrome instance
        ...
        SwitchBrowser   NEW     # following keywords will interact with latest opened browser (edge)
        ...
        SwitchBrowser   2       # following keywords will interact with firefox instance


    Related keywords
    ----------------
     \`OpenBrowser\,  \`CloseBrowser\,  \`SwitchWindow\, \`GetWebElement\`
    """
    browser.set_current_browser(index)


def _sessions_open() -> int:
    sessions = browser.get_open_browsers()
    return len(sessions)


def _close_remote_browser_session(driver: WebDriver, close_only: bool = False) -> bool:
    driver_type = str(type(driver))
    if 'remote.webdriver' in driver_type:
        session_id = driver.session_id
        remote_session_id = util.get_rfw_variable_value('${BROWSER_REMOTE_SESSION_ID}')
        if remote_session_id:
            logger.debug('Closing remote session id: {}, target session: {}'.format(
                remote_session_id, session_id))
            driver.session_id = remote_session_id
            driver.close()
            if not close_only:
                driver.quit()
            driver.session_id = session_id

            logger.warn('Browser re-use might leave oprhant chromedriver processes running. '
                        'Please check manually and close.')
            return True

    return False


@keyword(tags=("Browser", "Interaction"))
def close_browser() -> None:
    r"""Close current browser.

    This will also close remote browser sessions if open.

    Examples
    --------
     .. code-block:: robotframework

        CloseBrowser

    Related keywords
    ----------------
    \`CloseAllBrowsers\`, \`CloseRemoteBrowser\`, \`OpenBrowser\`
    """
    try:
        driver = browser.get_current_browser()
        if util.is_safari():
            safari.open_windows.clear()
        _close_remote_browser_session(driver, close_only=True)
        browser.remove_from_browser_cache(driver)

        # Clear browser re-use flag as no original session open anymore
        # not supported when running directly from Python
        BuiltIn().set_global_variable('${BROWSER_REUSE}', False)
        driver.quit()
    except QWebDriverError:
        logger.info("All browser windows already closed")
    except RobotNotRunningError:
        driver.quit()


@keyword(tags=("Browser", "Interaction", "Remote"))
def close_remote_browser() -> None:
    r"""Close remote browser session which is connected to the target browser.

    Closes only the remote browser session and leaves the target browser
    running. This makes it possible to continue using the existing browser
    for other tests.

    It is important to use this keyword to free up the resources i.e.
    unnecessary chrome instances are not left to run. However,
    it is good to monitor chromedriver processes as those might be still
    running.

    Examples
    --------
     .. code-block:: robotframework

        CloseBrowserSession

    Related keywords
    ----------------
    \`CloseAllBrowsers\`, \`CloseBrowser\`, \`OpenBrowser\`
    """
    try:
        driver = browser.get_current_browser()
        if _close_remote_browser_session(driver):
            browser.remove_from_browser_cache(driver)
    except QWebDriverError:
        logger.info("All browser windows already closed")


@keyword(tags=("Browser", "Interaction"))
def close_all_browsers() -> None:
    r"""Close all opened browsers.

    Examples
    --------
     .. code-block:: robotframework

        CloseAllBrowsers

    Related keywords
    ----------------
    \`CloseBrowser\`, \`CloseRemoteBrowser\`, \`OpenBrowser\`
    """
    drivers = browser.get_open_browsers()
    for driver in drivers:
        _close_remote_browser_session(driver, close_only=True)
        driver.quit()

    # remove everything from our cache so that they will not be there for next case.
    browser.clear_browser_cache()

    # Clear browser re-use flag as no session open anymore
    try:
        BuiltIn().set_global_variable('${BROWSER_REUSE}', False)
    except RobotNotRunningError:
        logger.debug("Only supported when run with Robot Framework")

    # safari specific
    safari.open_windows.clear()

    # Set 'Headless' flag as False, since no session open anymore
    CONFIG.set_value('Headless', False)


@keyword(tags=("Browser", "Verification"))
def verify_links(url: str = 'current', log_all: bool = False, header_only: bool = True) -> None:
    r"""Verify that all links on a given website return good HTTP status codes.

    Examples
    --------
    .. code-block:: robotframework

        VerifyLinks     https://qentinel.com/

    The above example verifies that all links work on qentinel.com

    .. code-block:: robotframework

        VerifyLinks     https://qentinel.com/       True

    The above example verifies that all links work on qentinel.com and logs the status of all the
    checked links.

    .. code-block:: robotframework

        VerifyLinks

    The above example verifies that all links work on on the current website.

    .. code-block:: robotframework

        VerifyLinks     header_only=False

    The above example verifies that all links work on on the current website.
    Argument **header_only=False** instructs QWeb to double-check 404/405's
    using GET method (by default only headers are checked).
    Headers should normally return same code as GET, but in some cases header can be configured
    intentionally to return something else.

    Parameters
    ----------
    url : str
        URL of the website that will be opened.
    log_all : bool
        Browser name. For example chrome, firefox or ie.
    header_only : bool
        True: check headers only (default)
        False: In case of header returning 404 or 405, double-check with GET

    Related keywords
    ----------------
    \`GoTo\`,\`VerifyTitle\`, \`VerifyUrl\`
    """
    if url == 'current':
        driver = browser.get_current_browser()
    else:
        window.go_to(url)
        driver = browser.get_current_browser()
    elements = driver.find_elements(By.XPATH, "//a[@href]")
    headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
    }
    checked = []
    broken = []
    logger.info('\nVerifying links on {}'.format(driver.current_url), also_console=True)
    for elem in elements:
        a_url = elem.get_attribute("href") or ""
        if util.url_validator(a_url) and a_url not in checked:
            try:
                r = requests.head(a_url, headers=headers)
                status = r.status_code
                if not header_only and status in [404, 405]:
                    r = requests.get(a_url, headers=headers)
                    status = r.status_code
            except requests.exceptions.ConnectionError as e:
                logger.error("{} can't be reached. Error message: {}".format(url, e))
                broken.append(a_url)
                continue
            if 399 < status < 600:
                error = 'Status of {} = {}'.format(a_url, status)
                logger.error(error)
                broken.append(a_url)
            elif status == 999:
                logger.info('Status of {} = {} (Linkedin specific error code. '
                            'Everything is probably fine.)'.format(a_url, status),
                            also_console=True)
            elif log_all:
                logger.info('Status of {} = {}'.format(a_url, status), also_console=True)
            checked.append(a_url)
    errors = len(broken)
    if len(checked) == 0:
        logger.warn('No links found.')
    if errors > 0:
        raise exceptions.QWebException('Found {} broken link(s): {}'.format(errors, broken))


def _browser_checker(browser_x: str, options: list[str], *args, **kwargs) -> WebDriver:
    """Determine the correct local browser in open_browser."""

    def use_chrome():
        return chrome.open_browser(chrome_args=options, **kwargs)

    def use_ff():
        return firefox.open_browser(firefox_args=options, *args, **kwargs)

    def use_safari():
        return safari.open_browser(*args, **kwargs)

    def use_android():
        return android.open_browser()

    def use_edge():
        return edge.open_browser(edge_args=options, **kwargs)

    browsers = {
        'chrome': use_chrome,
        'gc': use_chrome,
        'firefox': use_ff,
        'ff': use_ff,
        'safari': use_safari,
        'sf': use_safari,
        'android': use_android,
        'androidphone': use_android,
        'androidmobile': use_android,
        'edge': use_edge
    }
    try:
        return browsers[browser_x]()
    except KeyError:
        logger.error('Invalid browser name {}'.format(browser_x))
        raise
