from __future__ import annotations
import os
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.edge.options import Options as edge_options
from selenium.webdriver.firefox.options import Options as firefox_options
from selenium.webdriver.safari.options import Options as safari_options
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from typing import Any, Union
from robot.api import logger
from QWeb.internal import browser, exceptions, util

NAMES: dict[str, tuple[str, str]] = {
    # Default  versions for different browsers.
    'chrome': ('Chrome', 'latest'),
    'edge': ('Edge', 'latest'),
    'firefox': ('Firefox', 'latest'),
    'ff': ('Firefox', 'latest'),
    'safari': ('Safari', '16.5')
}

OS: dict[str, str] = {
    # Default versions for Windows and OSX.
    'osx': 'Ventura',
    'windows': '10'
}


def open_browser(bs_browser: str, project_name: str, run_id: str, **kwargs: Any) -> WebDriver:
    bs_key = util.get_rfw_variable_value('${APIKEY}') or os.environ.get('bskey')
    bs_user = util.get_rfw_variable_value('${USERNAME}') or os.environ.get('bsuser')
    bs_os = util.get_rfw_variable_value('${BSOS}') or 'windows'
    browser_name = util.get_rfw_variable_value('${BROWSER}') or NAMES[bs_browser][0]

    desired_caps: dict = {
        "buildName": project_name,
        "projectName": project_name,
        "sessionName": run_id,
        'os': bs_os,
        'osVersion': util.get_rfw_variable_value('${BSOSVERSION}') or OS[bs_os.lower()],
        'resolution': util.get_rfw_variable_value('${BSRESOLUTION}') or '1920x1080',
        "local": util.get_rfw_variable_value('${BSLOCAL}') or "false",
        "localIdentifier": util.get_rfw_variable_value('${BSLOCALID}') or '',
        **kwargs, }

    # handle issue where any, even empty value in localIdentifier turns local to true
    if desired_caps["local"] == 'false':
        del desired_caps["localIdentifier"]

    # create options instance based on selected browser
    options: Union[chrome_options, edge_options, firefox_options, safari_options]

    if browser_name == 'Chrome':
        options = chrome_options()
    elif browser_name == 'Edge':
        options = edge_options()
    elif browser_name == 'Firefox':
        options = firefox_options()
    elif browser_name == 'Safari':
        options = safari_options()
    else:
        raise exceptions.QWebException('Incorrect Browser name.')

    browser_version = util.get_rfw_variable_value('${BROWSERVERSION}') or NAMES[bs_browser][1]
    options.set_capability('browserVersion', browser_version)
    options.set_capability('bstack:options', desired_caps)

    try:
        executor_url = f'https://{bs_user}:{bs_key}@hub-cloud.browserstack.com/wd/hub'
        driver = webdriver.Remote(command_executor=executor_url, options=options)
        logger.info(f'BrowserStack session ID: {driver.session_id}', also_console=True)
    except WebDriverException as e:
        logger.error(e)
        raise exceptions.QWebException('Incorrect Browserstack capabilities.')
    browser.cache_browser(driver)
    return driver
