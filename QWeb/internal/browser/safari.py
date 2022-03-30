from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from QWeb.internal import browser

NAMES = ["safari", "sf"]
open_windows = []


def open_browser(port=0, executable_path='/usr/bin/safaridriver',
                 reuse_service=False, desired_capabilities=None, quiet=False):

    desired_capabilities = DesiredCapabilities.SAFARI

    driver = webdriver.Safari(port, executable_path, reuse_service,
                              desired_capabilities, quiet)
    driver.maximize_window()
    browser.cache_browser(driver)
    open_windows.append(driver.current_window_handle)
    return driver
