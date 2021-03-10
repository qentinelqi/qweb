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

import os
import pkg_resources
import requests
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from QWeb.keywords import window
from QWeb.internal import browser, xhr, exceptions, util
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.browser import chrome, firefox, ie, android, bs_mobile,\
                                  bs_desktop, safari, edge


def return_browser():
    """Return browser instance.

    Use this function if you need to expand QWeb and require direct browser access.

    Examples
    --------
     .. code-block:: robotframework

        ReturnBrowser
    """
    return browser.get_current_browser()


def open_browser(url, browser_alias, options=None, **kwargs):
    """Open new browser to given url.

    Uses the Selenium2Library open_browser method if the browser is not Chrome.

    For Chrome, recognizes if we are inside docker container and sets chrome
    capabilities accordingly.

    Browser options can also be given in the robot command, for example:
    robot -v browser_options:"--kiosk, --disable-gpu" testytest.robot

    Examples
    --------
     .. code-block:: robotframework

        OpenBrowser    http://google.com     chrome
        #Use Chromium instead of Chrome:
        OpenBrowser    http://google.com     chrome    chrome_path=/path/to/chromium/chrome.exe
        OpenBrowser    http://google.com     chrome    executable_path=/path/to/my/chromedriver.exe
        OpenBrowser    file://resources/window.html    firefox
        OpenBrowser    http://google.com     chrome    --allow-running-insecure-content, --xyz
        OpenBrowser    http://google.com     chrome    prefs="opt1":"True", "opt2":"False"
        OpenBrowser    http://google.com     firefox   -headless, -private, -xyz
        OpenBrowser    http://google.com     firefox   prefs="option1":"value1", "option2":"value2"
        OpenBrowser    http://google.com     firefox   -profile /path/to/profile
        OpenBrowser    http://google.com     firefox   -private    prefs="option1":"value1"
        #Supply preferences from a dictionary
        ${prefs_d}=    Create Dictionary     option1    value1    option2    value2
        OpenBrowser    http://google.com     firefox    prefs=${prefs_d}


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
        prefs=args: Experimental options for chrome browser.

    Raises
    ------
    ValueError
        Unkonown browser type
    """
    try:
        logger.info('\nQWeb version number: {}'.format(pkg_resources.get_distribution
                                                       ('QWeb').version), also_console=True)
    except pkg_resources.DistributionNotFound:
        logger.info('Could not find QWeb version number.')
    number_of_open_sessions = _sessions_open()
    if number_of_open_sessions > 0:
        logger.warn('You have {} browser sessions already open'.format(number_of_open_sessions))
    options = util.option_handler(options)
    b_lower = browser_alias.lower()
    bs_project_name = BuiltIn().get_variable_value('${PROJECTNAME}') or ""
    bs_run_id = BuiltIn().get_variable_value('${RUNID}') or ""
    if os.getenv('QWEB_HEADLESS'):
        kwargs = dict(headless=True)
    if os.getenv('CHROME_ARGS') is not None:
        if options is None:
            options = os.getenv('CHROME_ARGS').split(',')
        else:
            options = options + os.getenv('CHROME_ARGS').split(',')
    logger.debug('Options: {}'.format(options))
    provider = BuiltIn().get_variable_value('${PROVIDER}')
    if provider in ('bs', 'browserstack'):
        bs_device = BuiltIn().get_variable_value('${DEVICE}')
        if not bs_device and b_lower in bs_desktop.NAMES:
            driver = bs_desktop.open_browser(b_lower, bs_project_name, bs_run_id)
        elif bs_device:
            driver = bs_mobile.open_browser(bs_device, bs_project_name, bs_run_id)
        else:
            raise exceptions.QWebException('Unknown browserstack browser {}'.format(browser_alias))
    else:
        driver = _browser_checker(b_lower, options, **kwargs)
    util.initial_logging(driver.capabilities)

    # If user wants to re-use Chrome browser then he/she has to give
    # variable BROWSER_REUSE=True. In that case no URL loaded needed as
    # user wants to continue with the existing browser session
    is_browser_reused = util.par2bool(
        BuiltIn().get_variable_value('${BROWSER_REUSE}')) or False
    if not (is_browser_reused and b_lower == 'chrome'):
        driver.get(url)
    xhr.setup_xhr_monitor()


def _sessions_open():
    sessions = browser.get_open_browsers()
    return len(sessions)


def _close_remote_browser_session(driver, close_only=False):
    driver_type = str(type(driver))
    if 'remote.webdriver' in driver_type:
        session_id = driver.session_id
        remote_session_id = BuiltIn().get_variable_value('${BROWSER_REMOTE_SESSION_ID}')
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


def close_browser():
    """Close current browser.

    This will also close remote browser sessions if open.

    Examples
    --------
     .. code-block:: robotframework

        CloseBrowser

    """
    driver = browser.get_current_browser()
    if driver is not None:
        _close_remote_browser_session(driver, close_only=True)
        browser.remove_from_browser_cache(driver)

        # Clear browser re-use flag as no original session open anymore
        BuiltIn().set_global_variable('${BROWSER_REUSE}', False)
        driver.quit()
    else:
        logger.info("All browser windows already closed")


def close_remote_browser():
    """Close remote browser session which is connected to the target browser.

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

    """
    driver = browser.get_current_browser()
    if driver is not None:
        if _close_remote_browser_session(driver):
            browser.remove_from_browser_cache(driver)
    else:
        logger.info("All browser windows already closed")


def close_all_browsers():
    """Close all opened browsers.

    Examples
    --------
     .. code-block:: robotframework

        CloseAllBrowsers

    """
    drivers = browser.get_open_browsers()
    for driver in drivers:
        _close_remote_browser_session(driver, close_only=True)
        driver.quit()

    # remove everything from our cache so that they will not be there for next case.
    browser.clear_browser_cache()

    # Clear browser re-use flag as no session open anymore
    BuiltIn().set_global_variable('${BROWSER_REUSE}', False)

    # Set 'Headless' flag as False, since no session open anymore
    CONFIG.set_value('Headless', False)


def verify_links(url='current', log_all=False):
    """Verify that all links on a given website return good HTTP status codes.

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
    """
    if url == 'current':
        driver = browser.get_current_browser()
    else:
        window.go_to(url)
        driver = browser.get_current_browser()
    elements = driver.find_elements_by_xpath("//a[@href]")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
    }
    checked = []
    broken = []
    logger.info('\nVerifying links on {}'.format(driver.current_url), also_console=True)
    for elem in elements:
        url = elem.get_attribute("href")
        if util.url_validator(url) and url not in checked:
            try:
                r = requests.head(url, headers=headers)
                status = r.status_code
                if status == 405:
                    r = requests.get(url, headers=headers)
                    status = r.status_code
            except requests.exceptions.ConnectionError:
                logger.error("{} can't be reached.".format(url))
                broken.append(url)
                continue
            if 399 < status < 600:
                error = 'Status of {} = {}'.format(url, status)
                logger.error(error)
                broken.append(url)
            elif status == 999:
                logger.info('Status of {} = {} (Linkedin specific error code. '
                            'Everything is probably fine.)'
                            .format(url, status), also_console=True)
            elif log_all:
                logger.info('Status of {} = {}'.format(url, status), also_console=True)
            checked.append(url)
    errors = len(broken)
    if len(checked) == 0:
        logger.warn('No links found.')
    if errors > 0:
        raise exceptions.QWebException('Found {} broken link(s): {}'.format(errors, broken))


def _browser_checker(browser_x, options, *args, **kwargs):
    """Determine the correct local browser in open_browser."""
    def use_chrome():
        return chrome.open_browser(chrome_args=options, **kwargs)

    def use_ff():
        return firefox.open_browser(firefox_args=options, *args, **kwargs)

    def use_ie():
        return ie.open_browser(*args)

    def use_safari():
        return safari.open_browser(*args)

    def use_android():
        return android.open_browser()

    def use_edge():
        return edge.open_browser(edge_args=options, **kwargs)

    browsers = {
        'chrome': use_chrome,
        'gc': use_chrome,
        'firefox': use_ff,
        'ff': use_ff,
        'ie': use_ie,
        'internet explorer': use_ie,
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
