from __future__ import annotations
import os
from typing import Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Chrome, Remote
from selenium.webdriver.chrome.options import Options
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from QWeb.internal import browser, user, util
from QWeb.internal.config_defaults import CONFIG

NAMES: list[str] = ["chrome", "gc"]


def check_browser_reuse(**kwargs: Any) -> tuple[bool, Optional[str], Optional[str]]:
    try:
        browser_reuse = util.par2bool(util.get_rfw_variable_value('${BROWSER_REUSE}')) or False
        session_id = kwargs.get('session_id', None) or \
            util.get_rfw_variable_value('${BROWSER_SESSION_ID}')
        executor_url = kwargs.get('executor_url', None) or \
            util.get_rfw_variable_value('${BROWSER_EXECUTOR_URL}')
        return browser_reuse, session_id, executor_url
    except RobotNotRunningError:
        pass

    return False, None, None


def write_browser_session_argsfile(session_id: str,
                                   executor_url: str,
                                   fname: str = 'browser_session.arg') -> str:
    robot_output = util.get_rfw_variable_value('${OUTPUT DIR}')
    args_fn = os.path.join(robot_output or os.getcwd(), fname)
    with open(args_fn, 'w') as args_file:
        args_file.write('-v BROWSER_REUSE:{}{}'.format(True, os.linesep))
        args_file.write('-v BROWSER_EXECUTOR_URL:{}{}'.format(executor_url, os.linesep))
        args_file.write('-v BROWSER_SESSION_ID:{}{}'.format(session_id, os.linesep))

    return args_fn


def open_browser(executable_path: str = "chromedriver",
                 chrome_args: Optional[list[str]] = None,
                 desired_capabilities: Optional[dict[str, Any]] = None,
                 **kwargs: Any) -> WebDriver:
    """Open Chrome browser instance and cache the driver.

    Parameters
    ----------
    executable_path : str (Default "chromedriver")
        path to the executable. If the default is used it assumes the
        executable is in the $PATH.
    port : int (Default 0)
        port you would like the service to run, if left as 0, a free port will
        be found.
    desired_capabilities : dict (Default None)
        Dictionary object with non-browser specific capabilities only, such as
        "proxy" or "loggingPref".
    chrome_args : Optional arguments to modify browser settings
    """
    options = Options()

    logger.debug('opt: {}'.format(options))
    # Gets rid of Devtools listening .... printing
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # If user wants to re-use existing browser session then
    # he/she has to set variable BROWSER_REUSE_ENABLED to True.
    # If enabled, then web driver connection details are written
    # to an argument file. This file enables re-use of the current
    # chrome session.
    #
    # When variables BROWSER_SESSION_ID and BROWSER_EXECUTOR_URL are
    # set from argument file, then OpenBrowser will use those
    # parameters instead of opening new chrome session.
    # New Remote Web Driver is created in headless mode.
    chrome_path = kwargs.get('chrome_path', None) or util.get_rfw_variable_value('${CHROME_PATH}')
    if chrome_path:
        options.binary_location = chrome_path
    browser_reuse, session_id, executor_url = check_browser_reuse(**kwargs)
    logger.debug('browser_reuse: {}, session_id: {}, executor_url:  {}'.format(
        browser_reuse, session_id, executor_url))
    if browser_reuse and session_id and executor_url:
        options.add_argument("headless")

        driver = Remote(command_executor=executor_url,
                        desired_capabilities=options.to_capabilities())
        BuiltIn().set_global_variable('${BROWSER_REMOTE_SESSION_ID}', driver.session_id)
        driver.session_id = session_id  # type: ignore
    else:
        if user.is_root():
            options.add_argument("no-sandbox")
        if chrome_args:
            if any('headless' in _.lower() for _ in chrome_args):
                CONFIG.set_value('Headless', True)
            for item in chrome_args:
                options.add_argument(item.lstrip())
        options.add_argument("start-maximized")
        options.add_argument("--disable-notifications")
        if 'headless' in kwargs:
            CONFIG.set_value('Headless', True)
            options.add_argument("headless")
        if 'prefs' in kwargs:
            tmp_prefs = kwargs.get('prefs')
            prefs = util.parse_prefs(tmp_prefs)
            options.add_experimental_option('prefs', prefs)
        if 'emulation' in kwargs:
            emulation = kwargs['emulation']
            emulate_device = util.get_emulation_pref(emulation)
            options.add_experimental_option("mobileEmulation", emulate_device)

        driver = Chrome(util.get_rfw_variable_value('${CHROMEDRIVER_PATH}') or executable_path,
                        options=options,
                        desired_capabilities=desired_capabilities)

        browser_reuse_enabled = util.par2bool(
            util.get_rfw_variable_value('${BROWSER_REUSE_ENABLED}')) or False
        if browser_reuse_enabled:
            # Write WebDriver session info to RF arguments file for re-use
            write_browser_session_argsfile(driver.session_id, driver.command_executor._url)  # type: ignore # pylint: disable=protected-access,line-too-long

            # Clear possible existing global values
            BuiltIn().set_global_variable('${BROWSER_SESSION_ID}', None)
            BuiltIn().set_global_variable('${BROWSER_EXECUTOR_URL}', None)

    browser.cache_browser(driver)
    return driver
