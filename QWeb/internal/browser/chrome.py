from __future__ import annotations
import os
import subprocess
from typing import Optional, Any, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from QWeb.internal import browser, user, util
from QWeb.internal.config_defaults import CONFIG

NAMES: list[str] = ["chrome", "gc"]


def check_browser_reuse(**kwargs: Any) -> tuple[bool, Optional[str], Optional[str]]:
    try:
        browser_reuse = util.par2bool(util.get_rfw_variable_value("${BROWSER_REUSE}")) or False
        dbg_addr = kwargs.get("debugger_address", None) or util.get_rfw_variable_value(
            "${BROWSER_DEBUGGER_ADDRESS}"
        )
        executor_url = kwargs.get("executor_url", None) or util.get_rfw_variable_value(
            "${BROWSER_EXECUTOR_URL}"
        )
        return browser_reuse, dbg_addr, executor_url
    except RobotNotRunningError:
        pass

    return False, None, None


def write_browser_session_argsfile(
    dbg_addr: str, executor_url: str, fname: str = "browser_session.arg"
) -> str:
    robot_output = util.get_rfw_variable_value("${OUTPUT DIR}")
    args_fn = os.path.join(robot_output or os.getcwd(), fname)
    with open(args_fn, "w") as args_file:
        args_file.write(f"-v BROWSER_REUSE:{True}{os.linesep}")
        args_file.write(f"-v BROWSER_DEBUGGER_ADDRESS:{dbg_addr}{os.linesep}")
        args_file.write(f"-v BROWSER_EXECUTOR_URL:{executor_url}{os.linesep}")

    return args_fn


def open_browser(
    executable_path: str = "", chrome_args: Optional[list[str]] = None, **kwargs: Any
) -> WebDriver:
    """Open Chrome browser instance and cache the driver.

    Parameters
    ----------
    executable_path : str (Default "chromedriver")
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
    options = create_chrome_options(chrome_args, **kwargs)
    chromedriver_path = resolve_chromedriver_path(executable_path)

    browser_reuse, debugger_address, executor_url = check_browser_reuse(**kwargs)
    logger.debug(
        f"browser_reuse: {browser_reuse}, "
        f"executor_url: {executor_url}, "
        f"debugger_address: {debugger_address}"
    )

    if browser_reuse and executor_url and debugger_address:
        return create_reused_browser(debugger_address)

    driver = create_new_browser(chromedriver_path, options, **kwargs)
    cache_browser_session(driver)

    browser.cache_browser(driver)
    return driver


def create_chrome_options(chrome_args: Optional[list[str]], **kwargs: Any) -> Options:
    """Create Chrome options based on arguments and keyword arguments."""
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if chrome_args:
        if any("headless" in arg.lower() for arg in chrome_args):
            CONFIG.set_value("Headless", True)
        for arg in chrome_args:
            options.add_argument(arg.lstrip())

    maximize = kwargs.pop("maximize", True)
    if util.par2bool(maximize):
        options.add_argument("start-maximized")  # pylint: disable=no-member
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-search-engine-choice-screen")

    # page load strategy
    page_load_strategy = kwargs.pop("page_load_strategy", "normal")
    options.page_load_strategy = page_load_strategy

    if "headless" in kwargs:
        CONFIG.set_value("Headless", True)
        options.add_argument("headless")

    if "prefs" in kwargs:
        prefs = util.parse_prefs(kwargs.get("prefs"))
        options.add_experimental_option("prefs", prefs)

    if "emulation" in kwargs:
        emulate_device = util.get_emulation_pref(kwargs["emulation"])
        options.add_experimental_option("mobileEmulation", emulate_device)

    chrome_path = kwargs.get("chrome_path", None) or util.get_rfw_variable_value("${CHROME_PATH}")
    if chrome_path:
        options.binary_location = chrome_path

    chrome_version = (
        kwargs.get("browser_version", None)
        or util.get_rfw_variable_value("${BROWSER_VERSION}")
    )
    if chrome_version:
        options.browser_version = chrome_version

    if user.is_root():
        options.add_argument("no-sandbox")

    return options


def resolve_chromedriver_path(executable_path: str) -> str:
    """Resolve the path to the ChromeDriver executable."""
    driver_path = util.get_rfw_variable_value("${CHROMEDRIVER_PATH}") or executable_path
    if driver_path:
        logger.debug(f"Chromedriver path: {driver_path}")
    return driver_path


def create_reused_browser(debugger_address: str) -> WebDriver:
    """Create a browser instance reusing an existing session."""
    options = Options()
    options.add_argument("headless")
    options.debugger_address = debugger_address
    service = Service()
    return Chrome(service=service, options=options)


def create_new_browser(chromedriver_path: str, options: Options, **kwargs: Any) -> WebDriver:
    """Create a new browser instance."""
    log_level = kwargs.pop("log_level", None)
    log_output = kwargs.pop("log_output", None)
    remote_url = kwargs.get("remote_url")
    if remote_url:
        return WebDriver(command_executor=remote_url, options=options)

    service = build_chromium_service(Service, chromedriver_path, log_level, log_output)
    return Chrome(service=service, options=options)


def build_chromium_service(
    service_cls,
    executable_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_output: Optional[Union[str, int]] = None,
) -> Any:
    """Construct a ChromeDriver Service with optional logging."""
    # Auto-default log_level if only output is given
    if log_output and not log_level:
        log_level = "ALL"

    if isinstance(log_output, str) and log_output.upper() in ["CONSOLE",
                                                              "STDOUT",
                                                              "SUBPROCESS.STDOUT"]:
        log_output = subprocess.STDOUT
    service_args = [f"--log-level={log_level}"] if log_level else None

    kwargs: dict[str, Any] = {}
    if executable_path:
        kwargs["executable_path"] = executable_path
    if service_args:
        kwargs["service_args"] = service_args
    if log_output:
        kwargs["log_output"] = log_output

    return service_cls(**kwargs)


def cache_browser_session(driver: WebDriver) -> None:
    """Cache the WebDriver session info for reuse."""
    browser_reuse_enabled = (
        util.par2bool(util.get_rfw_variable_value("${BROWSER_REUSE_ENABLED}")) or False
    )
    if browser_reuse_enabled:
        dbg_address = driver.capabilities["goog:chromeOptions"]["debuggerAddress"]
        write_browser_session_argsfile(dbg_address, driver.service.service_url)  # type: ignore
        BuiltIn().set_global_variable("${BROWSER_EXECUTOR_URL}", None)
        BuiltIn().set_global_variable("${BROWSER_DEBUGGER_ADDRESS}", None)
