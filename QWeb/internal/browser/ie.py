from __future__ import annotations
from typing import Optional, Any, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.ie.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from QWeb.internal import browser

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
    options = Options()
    options.ignore_zoom_level = True
    options.require_window_focus = True
    options.ignore_protected_mode_settings = True
    options.native_events = False
    options.enable_persistent_hover = True
    options.ensure_clean_session = True
    options.javascript_enabled = True
    driver = webdriver.Ie(executable_path, capabilities, port, timeout, host,
                          log_level, log_file, options, ie_options)

    browser.cache_browser(driver)
    return driver
