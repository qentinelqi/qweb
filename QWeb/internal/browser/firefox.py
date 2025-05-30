from __future__ import annotations
from typing import Optional, Any, Union

import logging
from logging import Logger
import os
import subprocess

from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from QWeb.internal import browser, util
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal.exceptions import QWebValueError
from robot.api import logger

LOGGER: Logger = logging.getLogger(__name__)

NAMES: list[str] = ["firefox", "ff"]


# pylint: disable=too-many-branches
def open_browser(
    headless: bool = False,
    binary: Optional[str] = None,
    driver_path: str = "",
    firefox_args: Optional[list[str]] = None,
    **kwargs: Any,
) -> WebDriver:
    """Open Firefox browser and cache the driver.

    Parameters
    ----------
    binary : FirefoxBinary or str
        If string then is needs to be the absolute path to the binary. If
        undefined, the system default Firefox installation will be used.
    timeout : int
        Time to wait for Firefox to launch when using the extension connection.
    capabilities : dict
        Dictionary of desired capabilities.
    executable_path : str (Default geckodriver)
        Full path to override which geckodriver binary to use for Firefox
        47.0.1 and greater, which defaults to picking up the binary from the
        system path.
    log_path : str (Default "geckdriver.log")
        Where to log information from the driver.
    firefox_args : list
        Optional arguments to modify browser settings.
        https://developer.mozilla.org/en-US/docs/Mozilla/Command_Line_Options
    """
    options = Options()
    if headless:
        logger.warn(
            "Deprecated.\n"
            "Headless mode can be activated just like any other firefox option:\n"
            '"OpenBrowser   https://qentinel.com    ${BROWSER}   -headless"'
        )
        options.add_argument("-headless")
        CONFIG.set_value("Headless", True)

    ff_version_kwarg = kwargs.get("browser_version", None)
    ff_version = ff_version_kwarg or util.get_rfw_variable_value("${BROWSER_VERSION}")
    if ff_version:
        options.browser_version = ff_version
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", browser.MIME_TYPES)
    options.set_preference("extensions.update.enabled", False)
    options.set_preference("app.update.enabled", False)
    options.set_preference("app.update.auto", False)
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("privacy.socialtracking.block_cookies.enabled", False)
    kwargs = {k.lower(): v for k, v in kwargs.items()}  # Kwargs keys to lowercase
    if "prefs" in kwargs:
        tmp_prefs = kwargs.get("prefs")
        prefs = util.parse_prefs(tmp_prefs)

        for item in prefs.items():  # type: ignore[union-attr]
            key, value = item[0], item[1]
            logger.info("Using prefs: {} = {}".format(key, value), also_console=True)
            if not isinstance(value, int) and value.isdigit():
                value = int(value)
            options.set_preference(key, value)
    if firefox_args:
        if any("headless" in _.lower() for _ in firefox_args):
            CONFIG.set_value("Headless", True)
        for option in firefox_args:
            option = option.strip()
            if option.startswith("-profile"):
                _parse_profile_option(option, options)
            elif option.startswith("-"):
                options.add_argument(option)
            else:
                logger.warn(
                    f'Firefox arguments start with "-". '
                    f'Argument "{option}" has incorrect format and was ignored'
                )

    if binary:
        options.binary_location = binary

    remote_url = kwargs.get("remote_url")
    log_output = kwargs.pop("log_output", None)
    log_level = kwargs.pop("log_level", None)
    if remote_url:
        driver = WebDriver(command_executor=remote_url, options=options)
    else:
        service = build_firefox_service(Service, driver_path, log_level, log_output)
        driver = webdriver.Firefox(service=service, options=options)
    if os.name == "nt":  # Maximize window if running on windows, doesn't work on linux
        driver.maximize_window()
    browser.cache_browser(driver)

    return driver


def build_firefox_service(
    service_cls,
    executable_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_output: Optional[Union[str, int]] = None,
) -> Service:
    """
    Create a Firefox WebDriver Service with optional logging configuration.
    Supports log level and log output settings.

    Firefox log levels: fatal, error, warn, info, config, debug, trace
    """

    # Default level if not explicitly set
    log_level = log_level or "info"
    log_level = log_level.lower()

    # Handle STDOUT or CONSOLE as log_output
    if isinstance(log_output, str) and log_output.upper() in ("CONSOLE", "STDOUT"):
        log_output = subprocess.STDOUT

    kwargs: dict[str, Any] = {}
    if executable_path:
        kwargs["executable_path"] = executable_path
    if log_output is not None:
        kwargs["service_args"] = ["--log", log_level]
        kwargs["log_output"] = log_output

    return service_cls(**kwargs)


def _get_profile_dir(option_str: str) -> Optional[str]:
    try:
        profile = option_str.split()[1]
        if not os.path.isdir(profile):
            raise QWebValueError("Profile path is not a valid path!!")
    except IndexError:
        profile = None

    return profile


def _parse_profile_option(option_str: str, options: Options):
    profile_dir = _get_profile_dir(option_str)
    if not profile_dir:
        raise ValueError(f"Profile directory could not be determined from option: {option_str}")
    options.add_argument("-profile")
    options.add_argument(profile_dir)
