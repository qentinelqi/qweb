from __future__ import annotations
from typing import Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from QWeb.internal import browser

NAMES: list[str] = ["safari", "sf"]
open_windows: list[str] = []


def open_browser(port: int = 0,
                 executable_path: str = '/usr/bin/safaridriver',
                 reuse_service: bool = False,
                 desired_capabilities: Optional[dict[str, Any]] = None,
                 quiet: bool = False) -> WebDriver:

    desired_capabilities = DesiredCapabilities.SAFARI

    driver = webdriver.Safari(port, executable_path, reuse_service, desired_capabilities, quiet)
    driver.implicitly_wait(0.1)
    driver.maximize_window()
    browser.cache_browser(driver)
    open_windows.append(driver.current_window_handle)
    return driver
