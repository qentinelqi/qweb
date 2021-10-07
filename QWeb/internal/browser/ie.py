from selenium import webdriver
from selenium.webdriver.ie.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from QWeb.internal import browser

NAMES = ["ie", "internet explorer"]


def open_browser(executable_path='IEDriverServer',
                 capabilities=None,
                 port=0, timeout=30, host=None, log_level=None, log_file=None,
                 options=None, ie_options=None):

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
