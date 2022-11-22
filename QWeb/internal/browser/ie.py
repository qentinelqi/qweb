from __future__ import annotations
from typing import Optional, Any, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.ie.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from QWeb.internal import browser
from robot.api import logger

NAMES: list[str] = ["ie", "internet explorer"]


def open_browser(
        executable_path: str = 'IEDriverServer',
        capabilities: Optional[dict[str, Any]] = None,
        port: int = 0,
        timeout: Union[int, float, str] = 30,
        # technically host can be an int representation of IP-addr
        host: Optional[Union[str, int]] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        options: Optional[Options] = None,
        ie_options: Optional[Options] = None) -> WebDriver:

    capabilities = DesiredCapabilities.INTERNETEXPLORER.copy()

    if ie_options is not None:
        options = ie_options
    else:
        options = Options()

    options.ignore_zoom_level = True
    # next option property is currently broken in selenium
    options.require_window_focus = True  # type: ignore
    options.ignore_protected_mode_settings = True
    options.native_events = False
    options.persistent_hover = True
    options.ensure_clean_session = True
    # options.javascript_enabled = True  # no such property
    driver = webdriver.Ie(executable_path, capabilities, port, timeout, host, log_level, log_file,
                          options)

    browser.cache_browser(driver)
    logger.warn('Deprecated.\n'
                'Internet Explorer has reached it\'s end of life on June 2022.\n'
                'IE support will be removed from QWeb 1.1.2023. \n'
                'Use Edge instead.')

    return driver
