from __future__ import annotations
import subprocess
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from robot.api import logger
from QWeb.internal import browser

NAMES: list[str] = ["android", "androidphone", "androidmobile"]


def open_browser() -> WebDriver:
    try:
        adb_output = subprocess.check_output(['adb', 'devices']).decode()
    except IOError as e:
        logger.error('Adb not installed or working incorrectly\n' + str(e))
        raise
    ss_type = 'false'
    devices = [
        x for x in adb_output.split() if x not in ('List', 'of', 'device', 'devices', 'attached')
    ]
    if len(devices) != 1:
        logger.error('Number of attached devices is not 1\n')
        raise ValueError
    if 'emulator' in devices:  # this is here so screenshots work on emulators
        ss_type = 'true'
    version = subprocess.check_output(['adb', 'shell',
                                       'getprop ro.build.version.release']).decode().strip()

    options = Options()
    options.set_capability('platformName', 'Android')
    options.set_capability('platformVersion', version)
    options.set_capability('deviceName', devices[0])
    options.set_capability('browserName', 'Chrome')
    options.set_capability('nativeWebScreenshot', ss_type)

    driver = webdriver.Remote(command_executor='http://localhost:4723/wd/hub',
                              options=options)
    browser.cache_browser(driver)
    return driver
