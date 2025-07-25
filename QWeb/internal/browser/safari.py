from __future__ import annotations
from typing import Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
from selenium import webdriver
from robot.api import logger

from QWeb.internal import browser


NAMES: list[str] = ["safari", "sf"]
open_windows: list[str] = []


def open_browser(
    port: int = 0,
    driver_path: str = "",
    desired_capabilities: Optional[dict[str, Any]] = None,
    quiet: bool = False,
    **kwargs: Any,
) -> WebDriver:
    options = Options()

    # page load strategy
    page_load_strategy = kwargs.pop("page_load_strategy", "normal")
    options.page_load_strategy = page_load_strategy

    # safari options can be given as desired_capabilities (dict)
    # Example:
    #   &{caps}=   Create Dictionary  safari:automaticInspection=True
    #   openbrowser  https://www.google.com  safari   desired_capabilities=${caps}
    if desired_capabilities:
        try:
            for k, v in desired_capabilities.items():
                options.set_capability(k, v)
        except AttributeError:
            logger.warn(
                "Safari options/desired capabilities "
                "should be given as a dictionary. Example:\n\n"
                "&{caps}=\tCreate Dictionary\tsafari:automaticInspection=True\n"
                "OpenBrowser\thttps://www.google.com\tsafari\tdesired_capabilities=${caps}"
            )

    remote_url = kwargs.get("remote_url", None)
    enable_logging = kwargs.get("enable_logging", False)
    # make sure this is not just a string
    if remote_url:
        driver = WebDriver(command_executor=remote_url, options=options)
    else:
        if driver_path:
            service = Service(driver_path, port=port, quiet=quiet, enable_logging=enable_logging)
        else:
            service = Service(port=port, quiet=quiet, enable_logging=enable_logging)

        driver = webdriver.Safari(service=service, options=options)

    # If implicit_wait is not > 0 Safaridriver starts raising TimeoutExceptions
    #    instead of proper exception types
    driver.implicitly_wait(0.1)
    driver.maximize_window()
    browser.cache_browser(driver)
    open_windows.append(driver.current_window_handle)
    return driver
