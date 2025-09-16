# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 -            Qentinel Group.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------
from __future__ import annotations
from typing import Union, Any, Callable, Optional, List

from QWeb.internal import browser, javascript
from QWeb.internal.browser.safari import NAMES as SAFARINAMES
from QWeb.internal.input_handler import INPUT_HANDLER as input_handler
from QWeb.internal.exceptions import QWebValueMismatchError, QWebUnexpectedConditionError
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
import json
import platform
import re
import subprocess


def par2bool(s: Union[bool, int, str]) -> bool:
    """
    Returns boolean (True, False) from given parameter.
    Accepts booleans, strings or integers.
    """
    if isinstance(s, str):
        s = s.lower()
    return s in ["true", "1", "on", True, 1]


def xpath_validator(locator: str) -> bool:
    """Checks if given locator is an xpath and returns boolean (True, False)"""
    # TODO: Make this more reliable
    if locator.lower().startswith(("xpath=", "/html", "//")):
        return True
    return False


def url_validator(url: str) -> bool:
    """Checks if given url is valid and returns boolean (True, False)"""
    regex = re.compile(
        # Django url validation regex
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, url) is not None


def calculate_interval(timeout_int: int) -> float:
    """Calculates interval based on timeout.

    Some customers require long timeouts and polling every 0.1s results
    very longs logs. Poll less often if timeout is large.
    """
    if timeout_int > 60:
        interval = 3.0
    elif timeout_int > 10:
        interval = 1.0
    else:
        interval = 0.1
    return interval


def set_window_size(pixels: str) -> tuple[int, int]:
    width_str, height_str = _parse_pixels(pixels)
    width = int(width_str)
    height = int(height_str)
    driver = browser.get_current_browser()
    driver.set_window_size(width, height)
    return width, height


def _parse_pixels(pixels: str, split: str = "x") -> tuple[str, str]:
    pixel_list = pixels.lower().split(split)
    if len(pixel_list) == 1:
        raise ValueError("Pixels needs to be given with '1920x1080' syntax")
    return pixel_list[0], pixel_list[1]


def set_input_handler(input_method: str) -> str:
    input_handler.input_method = input_method.lower()
    return input_method.lower()


def get_emulation_pref(device_or_dimension: str) -> dict[str, Any]:
    """Sets correct mobile emulation option string based on given input
    (existing device profile name or screen dimensions).
    """
    try:
        width_str, height_str = _parse_pixels(device_or_dimension)
        return {"deviceMetrics": {"width": int(width_str), "height": int(height_str)}}
    except ValueError:
        return {"deviceName": device_or_dimension}


def set_line_break(key: str) -> str:
    if key == "\ue000":
        current_browser = browser.get_current_browser().capabilities["browserName"]
        if current_browser == "firefox":
            key = ""
            input_handler.line_break_key = key
            logger.info(
                "\n\\ue000 line break does not work with Firefox, using empty string"
                " instead. It is recommended to use None instead of \\ue000."
            )
        else:
            input_handler.line_break_key = key
    elif key.lower() in ("none", "empty", "null"):
        key = ""
        input_handler.line_break_key = key
    else:
        input_handler.line_break_key = key
    return key


def set_clear_key(key: str) -> Optional[str]:
    if key.lower() == "none":
        input_handler.clear_key = None
    else:
        input_handler.clear_key = key
    return input_handler.clear_key


def highlight_validation(color: str) -> str:
    """Validates the given highligh color is among supported basic colors"""
    if color.lower() not in [
        "red",
        "green",
        "blue",
        "black",
        "orange",
        "yellow",
        "fuchsia",
        "lime",
        "olive",
        "teal",
        "purple",
        "navy",
        "aqua",
    ]:
        raise ValueError("Not a supported highlight color")
    return color


def get_substring(text: str, remove_newlines: bool = True, **kwargs) -> Union[int, float, str]:
    if "\xa0" in text:
        text = text.replace("\xa0", " ")
    start, end = kwargs.get("between", "{}???{}").format(0, len(text)).split("???")
    include_start = kwargs.get("include_locator", False)
    exclude_end = kwargs.get("exclude_post", True)
    start = get_index_of(text, start, include_start)
    end = get_index_of(text, end, exclude_end)
    if end == 0:
        end = len(text)
    if "from_start" in kwargs:
        end = start + int(kwargs.get("from_start"))  # type: ignore[arg-type]
    if "from_end" in kwargs:
        start = end - int(kwargs.get("from_end"))  # type: ignore[arg-type]
    logger.debug("substring start: {}".format(start))
    logger.debug("substring end: {}".format(end))
    if remove_newlines:
        text = str(text[start:end]).strip().replace("\n", "")
        text = text.replace("\r", "")
    try:
        if "int" in kwargs:
            num = float(text.replace(" ", "").replace(",", "."))
            return int(num)
        if "float" in kwargs:
            return float(text.replace(" ", "").replace(",", "."))
    except ValueError as e:
        raise QWebValueMismatchError("Unable to convert. Got exception: {}".format(e)) from e
    return text


def get_index_of(text: str, locator: str, condition: Union[bool, int, str]) -> int:
    try:
        return int(locator.strip())
    except ValueError:
        if locator.startswith("\\"):
            locator.replace("\\", "")
    index = text.find(locator.strip())
    if index > -1:
        if par2bool(condition) is False:
            index += len(locator)
        return index
    raise QWebValueMismatchError('File did not contain the text "{}"'.format(locator))


def is_py_func(text: str) -> bool:
    return bool("(" and ")" in text)  # pylint: disable=R1726


def is_retina() -> bool:
    if platform.system().lower() == "darwin":
        if "arm" in platform.machine().lower():
            return True

        if (
            subprocess.call(
                "system_profiler SPDisplaysDataType | grep -i 'retina'",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            == 0
        ):
            return True
    return False


def is_safari() -> bool:
    driver = browser.get_current_browser()
    return driver.capabilities["browserName"].lower() in SAFARINAMES


def get_browser_width() -> int:
    driver = browser.get_current_browser()
    size = driver.get_window_size()
    return size["width"]


def get_monitor_width() -> int:
    return javascript.execute_javascript("return screen.width")


def prefs_to_dict(prefs: Union[dict, str]) -> dict[str, Any]:
    if isinstance(prefs, dict):
        d = prefs
    else:
        prefs_j = "{" + prefs + "}"
        try:
            d = json.loads(prefs_j)
        except json.decoder.JSONDecodeError:
            try:
                d = _handle_old_style_prefs(prefs)
            except QWebUnexpectedConditionError as e:
                raise QWebUnexpectedConditionError(
                    "Invalid argument! Experimental opts should given in robot dict "
                    "or string in format: key1:value1, key2:value2"
                ) from e
    # handle booleans in string format
    for key, value in list(d.items()):
        if isinstance(value, str):  # Check if the value is a string
            value_lower = value.lower()
            if value_lower == "true":
                d[key] = True
            elif value_lower == "false":
                d[key] = False
    return d


def _handle_old_style_prefs(prefs: str) -> dict:
    d = {}
    val: Union[bool, str]
    separated = prefs.split(",")
    for s in separated:
        splitted = s.split(":", maxsplit=1)
        if len(splitted) == 2:
            logger.warn("Prefs keys and values without quotes is deprecated.")
            key = splitted[0].strip()
            if "true" in splitted[1].lower() or "false" in splitted[1].lower():
                val = par2bool(splitted[1].strip())
            else:
                val = splitted[1].strip()
            d[key] = val
        else:
            raise QWebUnexpectedConditionError
    return d


def parse_prefs(prefs: Optional[Any]) -> dict:
    if isinstance(prefs, dict):
        return prefs

    return prefs_to_dict(str(prefs).strip())


def validate_run_before(value: Union[list[str], str]) -> Optional[Union[list[str], str]]:
    if isinstance(value, list):
        if value[0].lower().startswith("verify"):
            return value
    elif is_py_func(value):
        valid = ["verify_", "verify_no"]
        if any(x in value for x in valid):
            return value
    elif value.lower().startswith("verify"):
        return value
    logger.warn("Invalid value. Only Verify* keywords are accepted.")
    return None


def initial_logging(capabilities: dict[str, Any]) -> None:
    """Log version numbers at the start of test runs."""
    logger.debug(f"{capabilities}")
    try:
        b_n, b_v = capabilities["browserName"], capabilities["browserVersion"]
        logger.info("Browser: {}".format(b_n), also_console=True)
        logger.info("Browser version: {}".format(b_v), also_console=True)
        if b_n == "firefox":
            logger.info(
                "Geckodriver version: {}".format(capabilities["moz:geckodriverVersion"]),
                also_console=True,
            )
        if b_n == "chrome":
            logger.info(
                "Chromedriver version: {}".format(capabilities["chrome"]["chromedriverVersion"]),
                also_console=True,
            )
        if b_n == "msedge":
            logger.info(
                "Edgedriver version: {}".format(capabilities["msedge"]["msedgedriverVersion"]),
                also_console=True,
            )
    except KeyError:
        logger.debug("Could not get browser/driver version data.")


def option_handler(options: Optional[str]) -> list[str]:
    options2 = []
    if options:
        options2 += options.split(",")

    if get_rfw_variable_value("${BROWSER_OPTIONS}"):
        options2 += get_rfw_variable_value("${BROWSER_OPTIONS}").split(",")

    return options2


def get_rfw_variable_value(key: str, default_value=None) -> Any:
    """Return robot fw variable value if robot is running.
    Returns default value if robot is not running."""
    try:
        return BuiltIn().get_variable_value(key)
    except RobotNotRunningError:
        return default_value


def get_callable(pw: str) -> Callable[..., Any]:
    """Return function by Paceword name if exists."""
    lib = BuiltIn().get_library_instance("QWeb")
    pacewords = dir(lib)
    for paceword in pacewords:
        if not paceword.startswith("__"):
            if str(pw).replace(" ", "").lower() == paceword.replace("_", ""):
                fn = getattr(lib, paceword)
                return fn
    raise QWebUnexpectedConditionError("Paceword {} not found".format(pw))


def escape_xpath_quotes(text: str) -> str:
    """Return xpath text with proper quotes"""
    # both single and double quotes in text
    if '"' in text and "'" in text:
        return "concat(%s)" % ", '\"',".join('"%s"' % x for x in text.split('"'))
    # only double
    if '"' in text:
        return f"'{text}'"
    return f'"{text}"'


def anchor_to_index(anchor: str) -> int:
    try:
        index = int(anchor) - 1
    except ValueError:
        index = 0
    return index


def remove_duplicates_from_list(new_list: list, result_list: list) -> list:
    #  remove duplicates (normal search and including shadow search)
    for el in new_list:
        if result_list is not None and el not in list(result_list):
            result_list.append(el)
    return result_list


def remove_stale_elements(elems: Optional[List[WebElement]]) -> Optional[List[WebElement]]:
    if elems is None:
        return None
    # remove staling elements from original list
    for elem in reversed(elems):
        try:
            elem.text
        except (StaleElementReferenceException, NoSuchElementException):
            elems.remove(elem)
    return elems


def validate_ms(value: int | str) -> str:
    """
    Normalize milliseconds value for config storage.
    Always stored as '<int>ms', non-negative.
    """
    if isinstance(value, int):
        if value < 0:
            raise ValueError("Milliseconds must be non-negative.")
        return f"{value}ms"

    if isinstance(value, str):
        v = value.strip().lower().replace(" ", "")
        if v.endswith("ms"):
            v = v[:-2]
        try:
            n = int(v)
        except ValueError as e:
            raise ValueError(f"Invalid millisecond value: {value!r}") from e
        if n < 0:
            raise ValueError("Milliseconds value must be non-negative.")
        return f"{n}ms"

    raise ValueError(f"Invalid millisecond value: '{value}'")


def parse_ms(value: str) -> int:
    """Convert a canonical '<int>ms' string into an int."""
    v = value.strip().lower().replace(" ", "")
    v = v.removesuffix("ms")
    try:
        n = int(v)
    except ValueError as e:
        raise ValueError(f"Invalid millisecond value: {value!r}") from e
    return n


def validate_wait_strategy(value: str) -> str:
    """Validate and normalize wait strategy values."""
    valid_strategies = ["enhanced", "legacy"]
    if value.lower() not in valid_strategies:
        raise ValueError(f"Invalid wait strategy: {value!r}. Must be one of: {valid_strategies}")
    return value.lower()
