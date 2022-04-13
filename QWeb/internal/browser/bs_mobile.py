from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from QWeb.internal import browser, exceptions
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
import os

def open_browser(bs_device: str, project_name: str, run_id: str) -> WebDriver:
    desired_cap = {
        'build': project_name,
        'project': project_name,
        'name': run_id,
        'device': bs_device,
        'real_mobile': 'true',
        'browserstack.local': BuiltIn().get_variable_value('${BSLOCAL}') or 'false',
        'browserstack.localIdentifier': BuiltIn().get_variable_value('${BSLOCALID}') or ''
    }
    bs_key = BuiltIn().get_variable_value('${APIKEY}') or os.environ.get('bskey')
    bs_user = BuiltIn().get_variable_value('${USERNAME}') or os.environ.get('bsuser')

    try:
        driver = webdriver.Remote(
            command_executor='http://{}:{}@hub.browserstack.com:80/wd/hub'.format(bs_user, bs_key),
            desired_capabilities=desired_cap)
    except WebDriverException as e:
        logger.error(e)
        raise exceptions.QWebException('Incorrect Browserstack capabilities.')
    browser.cache_browser(driver)
    return driver
