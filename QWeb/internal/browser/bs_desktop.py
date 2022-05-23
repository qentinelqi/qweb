from __future__ import annotations
import os
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from typing import Any
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from QWeb.internal import browser, exceptions

NAMES: dict[str, tuple[str, str]] = {
    # Default  versions for different browsers.
    'chrome': ('Chrome', 'latest'),
    'ie': ('IE', 'latest'),
    'internet explorer': ('IE', 'latest'),
    'edge': ('Edge', 'latest'),
    'firefox': ('Firefox', 'latest'),
    'ff': ('Firefox', 'latest'),
    'safari': ('Safari', '15.3')
}

OS: dict[str, str] = {
    # Default versions for Windows and OSX.
    'osx': '"Big Sur',
    'windows': '10'
}


def open_browser(bs_browser: str, project_name: str, run_id: str, **kwargs: Any) -> WebDriver:
    bs_key = BuiltIn().get_variable_value('${APIKEY}') or os.environ.get('bskey')
    bs_user = BuiltIn().get_variable_value('${USERNAME}') or os.environ.get('bsuser')
    bs_os = BuiltIn().get_variable_value('${BSOS}') or 'windows'

    desired_caps:dict = {
        'bstack:options': {
            "buildName": project_name,
            "projectName": project_name,
            "sessionName": run_id,
            'os': bs_os,
            'osVersion': BuiltIn().get_variable_value('${BSOSVERSION}') or OS[bs_os.lower()],
            'resolution': BuiltIn().get_variable_value('${BSRESOLUTION}') or '1920x1080',
            "local": BuiltIn().get_variable_value('${BSLOCAL}') or "false",
            "localIdentifier": BuiltIn().get_variable_value('${BSLOCALID}') or '',
            **kwargs,
        },

        'browserName': BuiltIn().get_variable_value('${BROWSER}') or NAMES[bs_browser][0],
        'browserVersion': BuiltIn().get_variable_value('${BROWSERVERSION}') or NAMES[bs_browser][1]
    }

    # handle issue where any, even empty value in localIdentifier turns local to true
    if desired_caps["bstack:options"]["local"] == 'false':
        del desired_caps["bstack:options"]["localIdentifier"]

    try:
        executor_url = f'https://{bs_user}:{bs_key}@hub-cloud.browserstack.com/wd/hub'
        driver = webdriver.Remote(command_executor=executor_url, desired_capabilities=desired_caps)
        logger.info(f'BrowserStack session ID: {driver.session_id}', also_console=True)
    except WebDriverException as e:
        logger.error(e)
        raise exceptions.QWebException('Incorrect Browserstack capabilities.')
    browser.cache_browser(driver)
    return driver
