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
from dataclasses import dataclass
from typing import Union, Optional

from robot.api import logger
from robot.api.deco import keyword
from selenium.common.exceptions import NoSuchWindowException
from QWeb.internal import browser, javascript, xhr, window, decorators, util
from QWeb.internal.browser.safari import open_windows
from QWeb.internal.exceptions import QWebDriverError, QWebValueError
from QWeb.internal.config_defaults import CONFIG
import platform


@dataclass
class TabInfo:
    index: int
    handle: str


@keyword(tags=("Browser", "Interaction"))
@decorators.timeout_decorator
def go_to(url: str, timeout: Union[int, float, str] = 0) -> None:  # pylint: disable=unused-argument
    r"""Switch current page to given url.

    Examples
    --------
    .. code-block:: robotframework

        GoTo    http://google.com
        GoTo    file://resources/window.html

    Parameters
    ----------
    url : str
        URL of the website that will be opened.

    Raises
    ------
    UnexpectedAlertPresentException
        If the page opens with alert popup

    Related keywords
    ----------------
    \`CloseAllBrowsers\`, \`CloseBrowser\`, \`OpenBrowser\`, \`OpenWindow\`, \`SwitchWindow\`
    """
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword to open browser first")
    driver.get(url)


@keyword(tags=("Browser", "Interaction", "Window"))
def open_window() -> str:
    r"""Open new tab.

    Uses javascript to do this so javascript has to be enabled.

    Examples
    --------
    .. code-block:: robotframework

        OpenWindow

    Returns
    -------
    str
        The handle of the newly opened window. This can be used later to switch to this window.

    Related keywords
    ----------------
    \`CloseAllBrowsers\`, \`CloseBrowser\`, \`CloseOthers\`, \`GoTo\`,
    \`OpenBrowser\`, \`SwitchWindow\`
    """
    handles_before = set(window.get_window_handles())
    script = "window.open()"
    javascript.execute_javascript(script)

    # make ordered list for safari
    if util.is_safari():
        # refresh all windows, not just the ones we have tracked as open
        window.append_new_windows_safari()

    # After opening new window
    handles_after = set(window.get_window_handles())
    logger.debug(f"available handles: {len(handles_after)}")

    # The new handle is the one in 'after' but not in 'before'
    new_handles = handles_after - handles_before
    if not new_handles:
        raise QWebDriverError("No new window was opened.")
    new_handle = new_handles.pop()
    window.switch_to_window(new_handle)

    try:
        xhr.setup_xhr_monitor()
    except QWebDriverError:
        logger.debug("XHR monitor threw exception. Bypassing jQuery injection")

    return window.get_current_window_handle()


@keyword(tags=("Browser", "Interaction", "Window"))
def close_others() -> None:
    r"""Close all windows except the first window.

    If you have a test that may open new windows, this keyword closes them
    and switches to the first window.

    Examples
    --------
    .. code-block:: robotframework

        CloseOthers

    Raises
    ------
    NoSuchWindowException
        If other windows cannot been closed

    Related keywords
    ----------------
    \`CloseBrowser\`, \`CloseWindow\`, \`GoTo\`, \`OpenWindow\`, \`SwitchWindow\`
    """
    window_handles = window.get_window_handles()
    logger.info(f"Current browser has {len(window_handles)} tabs")
    if len(window_handles) == 1:
        return
    driver = browser.get_current_browser()
    while len(window_handles) > 1:
        try:
            window_handle = window_handles.pop()
            window.switch_to_window(window_handle)
            driver.close()
        except NoSuchWindowException:
            logger.info("Failed to close window")
    first_window_handle = window_handles[0] if util.is_safari() else window_handles.pop()
    window.switch_to_window(first_window_handle)

    number_of_handles = len(window.get_window_handles())
    if number_of_handles != 1:
        raise ValueError(f"Expected 1 window open, found {number_of_handles}")


@keyword(tags=("Browser", "Interaction", "Window"))
def close_window() -> None:
    r"""Close current tab and switch context to another window handle.

    If you need to change to specific tab, use switch window keyword.

    Examples
    --------
    .. code-block:: robotframework

        CloseWindow

    Related keywords
    ----------------
    \`CloseBrowser\`, \`CloseOthers\`, \`GoTo\`, \`OpenWindow\`, \`SwitchWindow\`
    """
    driver = browser.get_current_browser()
    window_handles = window.get_window_handles()
    logger.info("Current browser has {} tabs".format(len(window_handles)))
    if len(window_handles) == 1:
        logger.info("Only one tab, handle closing without changing context")
        if util.is_safari():
            open_windows.clear()
        browser.remove_from_browser_cache(driver)  # remove from browser cache
        driver.close()
    else:
        logger.info("Multiple tabs open, can change window context to another one")
        current_window = window.get_current_window_handle()
        current_index = window_handles.index(current_window)
        logger.info("Current index {}".format(current_index))
        if util.is_safari():
            open_windows.remove(current_window)
        driver.close()
        # "refresh" window handles
        window_handles = window.get_window_handles()
        current_length = len(window_handles)
        logger.info("After closing, {} tabs remain open".format(current_length))
        # if current index is more than new length, move to last handle
        if current_index > (len(window_handles) - 1):
            window.switch_to_window(window_handles[(current_index - 1)])
        # move to next window (as browsers do)
        else:
            window.switch_to_window(window_handles[current_index])
        logger.info("Changed context to tab with url {}".format(window.get_url()))


@keyword(tags=("Browser", "Interaction", "Window"))
@decorators.timeout_decorator
def switch_window(target: str, timeout: Union[int, float, str] = 0) -> str:  # pylint: disable=unused-argument
    r"""Switch to another browser tab or window.

    **Usage:**
        - Use the window handle (as returned by `ListWindows`, `GetWindowHandle`, or `OpenWindow`)
          or the special keyword "NEW" whenever possible. This is the preferred method.
        - Alternatively, using an index is supported for simple cases, but please note that the
          index refers to the internal order of window handles, which may not match the visual
          order in the browser UI. The index can change if tabs are closed or re-ordered by the
          browser.
        - If you must use an index, it is recommended to run `ListWindows` first
          to verify the current order and index of tabs.

    Examples
    --------
    .. code-block:: robotframework

        ...
        ${tab_1}=       OpenWindow
        # ... click link that opens a new tab
        ${new_tab}=     SwitchWindow     NEW    # Switches to the latest opened tab (recommended)
        SwitchWindow    ${tab_1}                # Switches to a specific tab by handle (recommended)
        SwitchWindow    2                       # Switches to the tab at index 2 (see caveats above)
        SwitchWindow    ${new_tab}

    Parameters
    ----------
    target : str
        The tab to switch to. Can be:
            - The window handle string (recommended; use `ListWindows` to get handles)
            - The special keyword "NEW" to switch to the latest opened tab (recommended)
            - An integer index (as a string), starting from 1 (see caveats above)
    timeout : str | int
        How long to search before failing.

    Returns
    -------
    str
        The window handle of the switched tab.

    Raises
    ------
    QWebValueError
        If the window handle or title is not found.
    QWebDriverError
        If the index is out of range.

    Related keywords
    ----------------
    `ListWindows`, `OpenWindow`, `CloseBrowser`, `CloseWindow`, `CloseOthers`, `GoTo`
    """
    # safari specific, refresh windows not open by keywords
    if util.is_safari():
        window.append_new_windows_safari()
    window_handles = window.get_window_handles()
    logger.info("Current browser contains {} tabs".format(len(window_handles)))

    # switch by index
    if target.isdigit():
        if int(target) == 0:
            raise QWebValueError("SwitchWindow index starts at 1.")
        i = int(target) - 1
        if i < len(window_handles):
            correct_window_handle = window_handles[i]
            window.switch_to_window(correct_window_handle)
            return correct_window_handle
        raise QWebDriverError(
            f"Tried to select tab with index {target} but there are only "
            f"{len(window_handles)} tabs open"
        )

    # switch to newest window
    if target == "NEW":
        window.switch_to_window(window_handles[-1])
        return window.get_current_window_handle()

    # switch by handle
    try:
        window_handles.index(target)
        window.switch_to_window(target)
        return target
    except ValueError as ve:
        logger.debug(f"Switching to window by handle failed: {target}")
        raise QWebValueError(f'Could not find window "{target}"') from ve


@keyword(tags=("Browser", "Getters", "Window"))
def list_windows() -> list[TabInfo]:
    r"""Lists all open window handles in the current browser.

    Each item in the returned list is a TabInfo dataclass containing:

    * index (the order of the tab in the browser, starting from 1)
    * handle (the unique identifier of the currently open page in that tab)

    Examples
    --------
    .. code-block:: robotframework

        ${open_tabs}=    ListWindows
    """
    handles = window.get_window_handles()
    return [TabInfo(idx + 1, tab) for idx, tab in enumerate(handles)]


@keyword(tags=("Browser", "Getters", "Window"))
def get_window_handle() -> str:
    r"""Gets the handle of the current browser window/tab.

    Examples
    --------
    .. code-block:: robotframework

        ${handle}=    GetWindowHandle

    Returns
    -------
    str
        The window handle of the current browser window/tab.
    """
    return window.get_current_window_handle()


def set_window_size(width: int, height: int) -> None:
    """*DEPRECATED!!* Use keyword `SetConfig` instead.

    Set current window size.

    Examples
    --------
     .. code-block:: robotframework

        SetWindowSize     1920    1080


    Parameters
    ----------
    width : int
        The width value of the window
    height: int
        The height value of the window
    """
    width = int(width)
    height = int(height)
    driver = browser.get_current_browser()
    driver.set_window_size(width, height)


@keyword(tags=("Browser", "Interaction", "Window"))
def maximize_window() -> None:
    r"""Maximizes current browser window.

    Note: This keyword will not fail if maximizing is prevented for some reason.
          This can happen for example if window manager is not installed or setup correctly.

    Examples
    --------
     .. code-block:: robotframework

        MaximizeWindow


    Parameters
    ----------
    None

    Related keywords
    ----------------
    \`Back\`,\`RefreshPage\`, \`OpenWindow\`, \`SwitchWindow\`
    """
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword to open browser first")

    # workaround for linux driver errors
    is_linux = platform.system().lower() == "linux"

    if CONFIG.get_value("Headless") is True or is_linux:
        logger.debug("Maximizing browser in headless mode")
        screen_width_js = driver.execute_script("return screen.width")
        screen_height_js = driver.execute_script("return screen.height")

        driver.set_window_size(screen_width_js, screen_height_js)

    else:
        driver.maximize_window()

    size = driver.get_window_size()
    logger.debug("Window size set to {}x{}".format(size["width"], size["height"]))


@keyword(tags=("Browser", "Getters"))
def get_url() -> str:
    r"""Gets current url/location.


    Examples
    --------
     .. code-block:: robotframework

        ${url}=   GetUrl


    Parameters
    ----------
    None

    Related keywords
    ----------------
    \`GetTitle\`,\`VerifyTitle\`, \`VerifyUrl\`
    """
    return window.get_url()


@keyword(tags=("Browser", "Verification"))
@decorators.timeout_decorator
def verify_url(url: str, timeout: Union[int, float, str] = 0) -> None:  # pylint: disable=unused-argument
    r"""Verifies that current page url/location matches expected url.


    Examples
    --------
     .. code-block:: robotframework

        VerifyUrl      https://www.google.com
        VerifyUrl      https://www.google.com     timeout=5


    Parameters
    ----------
    url : str
        The expected url
    timeout : str | int
        How long we wait for url to change before failing.

    Raises
    ------
    QWebValueError
        If the expected url differs from current url

    Related keywords
    ----------------
    \`GetTitle\`, \`GetUrl\`, \`VerifyTitle\`
    """
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword to open browser first")
    current = driver.current_url

    if current.lower() != url.lower():
        raise QWebValueError(f"Current url '{current}'' does not match expected url '{url}'")


@keyword(tags=("Browser", "Getters"))
def get_title() -> str:
    r"""Gets the title of current page/window.


    Examples
    --------
     .. code-block:: robotframework

        ${title}=   GetTitle


    Parameters
    ----------
    None

    Related keywords
    ----------------
    \`GetUrl\`, \`VerifyTitle\`, \`VerifyUrl\`
    """
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword to open browser first")
    return driver.title


@keyword(tags=("Browser", "Verification"))
@decorators.timeout_decorator
def verify_title(title: str, timeout: Union[int, float, str] = 0) -> None:  # pylint: disable=unused-argument
    r"""Verifies that current page's title matches expected title.


    Examples
    --------
     .. code-block:: robotframework

        VerifyTitle      Google
        VerifyTitle      Google     timeout=3


    Parameters
    ----------
    title : str
        The expected title
    timeout : str | int
        How long we wait for title to change before failing.

    Raises
    ------
    QWebValueError
        If the expected title differs from actual page title

    Related keywords
    ----------------
    \`GetTitle\`, \`GetUrl\`, \`VerifyUrl\`
    """
    driver = browser.get_current_browser()
    if driver is None:
        raise QWebDriverError("No browser open. Use OpenBrowser keyword to open browser first")
    actual = driver.title

    if actual != title:
        raise QWebValueError(f"Page title '{actual}'' does not match expected '{title}'")


@keyword(tags=("Browser", "Interaction"))
def swipe_down(times: str = "1", start: Optional[str] = None) -> None:
    r"""Swipes down on the screen.

    Examples
    --------
    .. code-block:: robotframework

        SwipeDown   # Swipes down once
        SwipeDown   5   # Swipes down five times
        SwipeDown   1   Qentinel Touch  # Swipes down once, starting from the text "Qentinel Touch"
        SwipeDown   5   Qentinel Touch  # Swipes down five times, from the text "Qentinel Touch"

    Parameters
    ----------
    times : str
        The amount of times we swipe / length of the swipe
    start : str
        Optional starting point for the swipe

    Raises
    ------
    ValueError
        If the swipe amount is not an integer.

    Related keywords
    ----------------
    \`SwipeLeft\`, \`SwipeRight\`, \`SwipeUp\`
    """
    window.swipe("down", times, start)


@keyword(tags=("Browser", "Interaction"))
def swipe_up(times: str = "1", start: Optional[str] = None) -> None:
    r"""Swipes up on the screen.

    Examples
    --------
    .. code-block:: robotframework

        SwipeUp   # Swipes up once
        SwipeUp   5   # Swipes up five times
        SwipeUp   1   Qentinel Touch   # Swipes up once, from the text "Qentinel Touch"
        SwipeUp   5   Qentinel Touch    # Swipes up five times, from the text "Qentinel Touch"

    Parameters
    ----------
    times : str
        The amount of times swiped / length of the swipe
    start : str
        Optional starting point for the swipe

    Raises
    ------
    ValueError
        If the swipe amount is not an integer.

    Related keywords
    ----------------
    \`SwipeDown\`, \`SwipeLeft\`, \`SwipeRight\`
    """
    window.swipe("up", times, start)


@keyword(tags=("Browser", "Interaction"))
def swipe_left(times: str = "1", start: Optional[str] = None) -> None:
    r"""Swipes left on the screen.

    Examples
    --------
    .. code-block:: robotframework

        SwipeLeft   # Swipes left once
        SwipeLeft   5   # Swipes left five times
        SwipeLeft   1   Qentinel Touch   # Swipes left once, from the text "Qentinel Touch"
        SwipeLeft   5   Qentinel Touch   # Swipes left five times, from the text "Qentinel Touch"

    Parameters
    ----------
    times : str
        The amount of times swiped / length of the swipe
    start : str
        Optional starting point for the swipe

    Raises
    ------
    ValueError
        If the swipe amount is not an integer.

    Related keywords
    ----------------
    \`SwipeDown\`, \`SwipeRight\`, \`SwipeUp\`
    """
    window.swipe("left", times, start)


@keyword(tags=("Browser", "Interaction"))
def swipe_right(times: str = "1", start: Optional[str] = None) -> None:
    r"""Swipes right on the screen.

    Examples
    --------
    .. code-block:: robotframework

        SwipeRight   # Swipes right once
        SwipeRight   5   # Swipes right five times
        SwipeRight   1   Qentinel Touch   # Swipes right once, from the text "Qentinel Touch"
        SwipeRight   5   Qentinel Touch   # Swipes right five times, from the text "Qentinel Touch"

    Parameters
    ----------
    times : str
        The amount of times swiped / length of the swipe
    start : str
        Optional starting point for the swipe

    Raises
    ------
    ValueError
        If the swipe amount is not an integer.

    Related keywords
    ----------------
    \`SwipeDown\`, \`SwipeLeft\`, \`SwipeUp\`
    """
    window.swipe("right", times, start)
