from __future__ import annotations
from typing import Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from robot.api import logger
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal import browser, user, util
from QWeb.internal.browser.chrome import build_chromium_service

NAMES: list[str] = ["edge", "msedge"]


def open_browser(
    executable_path: str = "", edge_args: Optional[list[str]] = None, **kwargs: Any
) -> WebDriver:
    """Open Edge browser instance and cache the driver.

    Parameters
    ----------
    executable_path : str (Default "msedgedriver")
        path to the executable. If the default is used it assumes the
        executable is in the $PATH.
    port : int (Default 0)
        port you would like the service to run, if left as 0, a free port will
        be found.
    desired_capabilities : dict (Default None)
        Dictionary object with non-browser specific capabilities only, such as
        "proxy" or "loggingPref".
    chrome_args : Optional arguments to modify browser settings
    """
    options = create_edge_options(edge_args, **kwargs)

    edgedriver_path = util.get_rfw_variable_value("${EDGEDRIVER_PATH}") or executable_path
    if edgedriver_path:
        logger.debug(f"Edgedriver path: {edgedriver_path}")
    edge_path = kwargs.get("edge_path", None) or util.get_rfw_variable_value("${EDGE_PATH}")
    if edge_path:
        options.binary_location = edge_path  # pylint: disable=no-member

    edge_version_kwarg = kwargs.get("browser_version", None)
    edge_version = edge_version_kwarg or util.get_rfw_variable_value("${BROWSER_VERSION}")

    if edge_version:
        options.browser_version = edge_version

    # Gets rid of Devtools listening .... printing
    # other non-sensical error messages

    remote_url = kwargs.get("remote_url", None)
    log_level = kwargs.pop("log_level", None)
    log_output = kwargs.pop("log_output", None)
    if remote_url:
        driver = WebDriver(command_executor=remote_url, options=options)

    else:
        # same function as in Chrome
        service = build_chromium_service(Service,
                                         edgedriver_path,
                                         log_level,
                                         log_output)
        driver = Edge(service=service, options=options)

    browser.cache_browser(driver)
    return driver


def create_edge_options(edge_args: Optional[list[str]], **kwargs: Any) -> Options:
    """Create Chrome options based on arguments and keyword arguments."""
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # pylint: disable=no-member

    if user.is_root() or user.is_docker():
        options.add_argument("no-sandbox")  # pylint: disable=no-member
    if edge_args:
        if any("--headless" in _.lower() for _ in edge_args):
            CONFIG.set_value("Headless", True)
        for item in edge_args:
            options.add_argument(item.lstrip())  # pylint: disable=no-member
    maximize = kwargs.pop("maximize", True)
    if util.par2bool(maximize):
        options.add_argument("start-maximized")  # pylint: disable=no-member
    options.add_argument("--disable-notifications")  # pylint: disable=no-member

    # page load strategy
    page_load_strategy = kwargs.pop("page_load_strategy", "normal")
    options.page_load_strategy = page_load_strategy

    if "headless" in kwargs:
        CONFIG.set_value("Headless", True)
        options.add_argument("--headless")  # pylint: disable=no-member
    if "prefs" in kwargs:
        tmp_prefs = kwargs.get("prefs")
        prefs = util.parse_prefs(tmp_prefs)
        options.add_experimental_option("prefs", prefs)
        logger.warn("prefs: {}".format(prefs))

    if "emulation" in kwargs:
        emulation = kwargs["emulation"]
        emulate_device = util.get_emulation_pref(emulation)
        options.add_experimental_option("mobileEmulation", emulate_device)
    return options
