import os
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from typing import Any
from robot.api import logger
from QWeb.internal import browser, exceptions, util


def open_browser(bs_device: str, project_name: str, run_id: str, **kwargs: Any) -> WebDriver:

    desired_cap = {
        'bstack:options': {
            "buildName": project_name,
            "projectName": project_name,
            "sessionName": run_id,
            "deviceName": bs_device,
            "realMobile": "true",
            "local": util.get_rfw_variable_value('${BSLOCAL}') or "false",
            "localIdentifier": util.get_rfw_variable_value('${BSLOCALID}') or '',
            **kwargs,
        }
    }

    # handle issue where any, even empty value in localIdentifier turns local to true
    if desired_cap["bstack:options"]["local"] == 'false':
        del desired_cap["bstack:options"]["localIdentifier"]

    bs_key = util.get_rfw_variable_value('${APIKEY}') or os.environ.get('bskey')
    bs_user = util.get_rfw_variable_value('${USERNAME}') or os.environ.get('bsuser')

    try:
        driver = webdriver.Remote(
                 command_executor=f'http://{bs_user}:{bs_key}@hub.browserstack.com:80/wd/hub',
                 desired_capabilities=desired_cap)

        logger.info(f'BrowserStack session ID: {driver.session_id}', also_console=True)
    except WebDriverException as e:
        logger.error(e)
        raise exceptions.QWebException('Incorrect Browserstack capabilities.')
    browser.cache_browser(driver)
    return driver
