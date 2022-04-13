from __future__ import annotations
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from QWeb.internal import browser, exceptions
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
import os

NAMES: dict[str,tuple[str,str]] = {
    # Default  versions for different browsers.
    'chrome': ('Chrome', 'latest'),
    'ie': ('IE', '11'),
    'internet explorer': ('IE', '11'),
    'edge': ('Edge', '18.0'),
    'firefox': ('Firefox', '66.0'),
    'ff': ('Firefox', '66.0'),
    'safari': ('Safari', '13.0')
}

OS: dict[str,str] = {
    # Default versions for Windows and OSX.
    'osx': 'Catalina',
    'windows': '10'
}


def open_browser(bs_browser: str, project_name: str, run_id: str) -> WebDriver:
    bs_key = BuiltIn().get_variable_value('${APIKEY}') or os.environ.get('bskey')
    bs_user = BuiltIn().get_variable_value('${USERNAME}') or os.environ.get('bsuser')
    bs_os = BuiltIn().get_variable_value('${BSOS}') or 'windows'

    desired_caps = {
        'build': project_name,
        'project': project_name,
        'name': run_id,
        'os': bs_os,
        'resolution': BuiltIn().get_variable_value('${BSRESOLUTION}') or '1920x1080',
        'browserstack.local': BuiltIn().get_variable_value('${BSLOCAL}') or 'false',
        'browserstack.localIdentifier': BuiltIn().get_variable_value('${BSLOCALID}') or '',
        'os_version': BuiltIn().get_variable_value('${BSOSVERSION}') or OS[bs_os.lower()],
        'browser': BuiltIn().get_variable_value('${BROWSER}') or NAMES[bs_browser][0],
        'browser_version': BuiltIn().get_variable_value('${BROWSERVERSION}') or NAMES[bs_browser][1]
    }

    try:
        executor_url = 'https://{}:{}@hub-cloud.browserstack.com/wd/hub'.format(bs_user, bs_key)
        driver = webdriver.Remote(command_executor=executor_url, desired_capabilities=desired_caps)
    except WebDriverException as e:
        logger.error(e)
        raise exceptions.QWebException('Incorrect Browserstack capabilities.')
    browser.cache_browser(driver)
    return driver
