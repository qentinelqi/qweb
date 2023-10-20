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
from typing import Callable, Any
import traceback
import types
import time

from functools import wraps
import QWeb.config as custom_config

try:
    from QWeb.keywords import (alert, browser, window, frame, element, text, checkbox, input_,
                               javascript, screenshot, download, table, search_strategy, dropdown,
                               cookies, config, icon, dragdrop, lists, file, debug, ajax, blocks)

    from QWeb.internal import util
    from QWeb.internal.config_defaults import CONFIG
    from robot.api import logger
    from robot.utils import timestr_to_secs as _timestr_to_secs
    from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
    from robot.libraries import Dialogs

# Print system exit message. This can happen on fresh linux when tkinter
# dependencies are not installed. This is a workaround as normally system
# exit message is not cathced by robot framework / debugger.
except SystemExit as se:
    raise Exception(se)  # pylint: disable=W0707


class QWeb:
    r"""
    QWeb is a powerful and versatile `Robot Framework <https://robotframework.org/>`_ library that
    enables efficient and reliable web testing and automation. One of the key strengths of QWeb
    is its intuitive and user-friendly syntax, which makes it easy to write and maintain complex
    test cases.

    The library offers:

    - **Intuitive Syntax**: User-friendly syntax for writing and maintaining complex test cases.
    - **Smart locators**: Interact with web elements using natural language locators.
      | `Locators`_
    - **Anchors**: Used to pinpoint specific instances of web elements with the same locator.
      | `Anchors`_
    - **Visibility**: By default interacting with visible elements only, but allowing access to
      hidden elements when needed.
      | `Visibility`_
    - **Shadow DOM support**: Allows interaction with elements inside a shadow DOM, which are
      encapsulated from the main document.
      | `Shadow_dom`_
    - **Automatic waits**: Automatically handling latencies etc. via automatic wait times.
      | `Waits`_
    - **Automatic frame handling**: Automatically moving between frames and finding elements from
      any embedded frame.
    - And many more features...


    Driver Management
    -----------------
    QWeb uses the Selenium WebDriver internally to interact with a web browser.
    Since QWeb 3.0.0 / Selenium 4.10.0 `browser drivers` can be automatically downloaded and
    installed using Selenium Manager, provided that driver is not found in PATH.
    Alternatively you can still manually download and install drivers or let 3rd party
    utilities like Webdriver Manager do it for you.

    For Chrome `browser_version` can also be given; if your locally installed Chrome matches
    this version, it will be used. If not, a suitable version of `Chrome for Testing` will be
    automatically downloaded

    .. _Locators:

    Locator strategies
    ------------------
    One of the greatest conceptual difference of QWeb compared to other web test automation
    libraries is the use of UI texts as a locator when ever it’s possible.
    With UI text as a locator there is no need to inspect html source, you can just use what
    you see on the screen. On the other hand, textual locators are usually easier to maintain.

    There are situations where more complex locators (xpaths etc.) might be needed, but it’s
    usually a small portion of test cases / steps. If you notice yourself using xpaths in most
    steps, please consider re-factoring your test script implementation!

    Here are four ways of finding elements. These are presented in order of preference of using
    them:

    **Text**

    The most preferred way is using UI texts as locators. Examples:

    .. code-block:: robotframework

        *** Test Cases ***
        Example test case using textual locators
            OpenBrowser         https://qentinelqi.github.io/shop       chrome
            VerifyText          The animal friendly clothing company
            ClickText           Scar the Lion
            ...
            # finds input field based on label
            TypeText            Username        myusername@test.com

    **Attribute values**

    If there is no visible UI text available, it's possible to find elements using any attribute
    value the element has. In the simplest form you can hover over an element and see the alt
    text/title value, if available.

    Examples:

    .. code-block:: robotframework

        *** Test Cases ***
        Example test case using attribute values as locators
            OpenBrowser    hrrps://www.google.com      chrome
            # finds input field based on attribute title value
            TypeText            Search                     Copado Robotic Testing
            ClickItem           Clear search

    **Xpaths**

    Xpaths are also supported as locators. These are mostly used by QWords ending with
    ***Element**.

    .. code-block:: robotframework

        *** Test Cases ***
        Example test case using xpaths as locators
            OpenBrowser         https://qentinelqi.github.io/shop    chrome
            VerifyElement       //ul[@class\="product-list"]
            ClickText           Our Story
            VerifyNoElement     xpath\=//ul[@class\="product-list"]

    .. caution:: Xpath locators or keywords using them do not work in Shadow DOM. If your
       web application uses Shadow DOM’s, use **\*Text** and **\*Item** keywords instead.

    **Icons / images**

    Bitmap/image comparison can also be used.
    In that case, you need to have a reference image and it will be found (or clicked) on
    a screen.
    Typically image comparison tends to be a bit harder to maintain.

    .. code-block:: robotframework

        *** Test Cases ***
        Example test case using reference image as locator
            SetConfig           LogMatchedIcons    True  # Log matched image to logs
            OpenBrowser         https://qentinelqi.github.io/shop    chrome
            VerifyIcon          paw.png
            ClickIcon           cart.png

    .. note:: Keywords for using icons/images have a naming convention **\*Icon**.
      (ClickIcon, VerifyIcon etc.)

    .. _Anchors:

    Anchors
    -------
    When a locator identifies multiple elements, ``anchors`` can be used to pinpoint a
    specific instance. Anchor can be another nearby text or a numeric index.

    .. code-block:: robotframework

        ClickText    Login      anchor=Cancel  # Textual anchor
        ClickText    Login      anchor=3       # Numeric anchor

    .. _Shadow_dom:

    Shadow DOM
    ----------
    Shadow DOM is a web standard that allows for encapsulation of styling and markup in web
    components. It's like a lightweight document inside the main document, with its own set of
    elements. Elements inside a shadow DOM are not directly accessible using traditional locators
    like XPath or CSS selectors.

    Special methods or settings are often required in automation frameworks to interact with
    elements inside a shadow DOM. QWeb provides support for elements inside a shadow DOM, which are
    encapsulated from the main document. To enable searching elements inside the shadow DOM, use:

    .. code-block:: robotframework

        SetConfig   ShadowDOM    True  # or 'on'

    .. tip::
       Any QWeb keyword accepting locator as a **text** or **attribute value** will work with
       elements inside a shadow DOM.

    .. important:: SetConfig ShadowDOM    True    must be used to enable element search inside
       a shadow DOM

    .. caution:: Some keywords, for example GetWebElement, work with many locator types.

    These keywords work with elements inside a shadow DOM when text or attribute values are used
    as a locator. Note that some of these keywords may require you to give an additional argument,
    for example:

    .. code-block:: robotframework

        SetConfig   ShadowDOM       True
        ${elem}     GetWebelement   Log In    element_type=text

    .. _Visibility:

    Visibility
    ----------
    In web automation, visibility refers to whether a web element is visible to the user or not.
    An element might exist in the DOM (Document Object Model) but may not be visible due to
    various reasons like CSS styles (e.g., display: none) or even by mistake.
    Automation frameworks often provide ways to interact only with visible elements,
    as invisible elements are typically not interactable by the user.

    QWeb by default finds only visible elements, but provides support for elements that are not
    visible by default.

    .. code-block:: robotframework

        ClickText   Login       visibility=False  # extend one element search to invisible elements

        SetConfig   Visibility  False  # extend element search to invisible elements globally

    .. _Waits:

    Automatic Wait Times
    --------------------
    QWeb automatically handles latencies by introducing wait times.
    This ensures that the automation script waits for the web elements to load or become
    interactable before performing actions, reducing the chances of test failures due to element
    not found or not interactable errors.

    There should not be reason to use **Sleep** keyword or such except in very exceptional cases.
    Almost all QWords have an inbuilt timeout, i.e they keep re-trying to find elements and do
    their action until action succeeds OR until timeout limit is reached.
    By default this timeout limit is 10 seconds.

    You can change this timeout temporarily by giving an argument timeout:

    .. code-block:: robotframework

        # only wait 3 seconds for element to appear
        VerifyText      Username    timeout=3

        # wait max 30 seconds for element to appear
        ClickText       Login       timeout=30

    You can also change timeouts for every keyword (globally) with SetConfig:

    .. code-block:: robotframework

        SetConfig       DefaultTimeout    60
        # would wait 60 seconds for text to appear before failing
        VerifyText      Username
        # would wait max 60 seconds for element to appear
        ClickText       Login

    .. tip:: It's preferable to use QWeb's automatic wait times instead of Sleep keyword.

       - **Sleep** keyword waits for the specified amount of time.
       - QWeb automatically waits until element is visible or until timeout limit is reached and
         then continue.

    """
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self, run_on_failure_keyword: str = "Log Screenshot") -> None:
        '''Initializes the QWeb library and adds all the keywords to the instance.

        - ``run_on_failure_keyword``:
          The keyword to run when a failure occurs. Default is "Log Screenshot".

        '''
        self._run_on_failure_keyword = run_on_failure_keyword
        for module in (alert, browser, window, frame, element, text, checkbox, input_, javascript,
                       screenshot, custom_config, download, search_strategy, table, dropdown,
                       cookies, config, icon, dragdrop, lists, file, debug, ajax, blocks):
            for name in dir(module):
                if not name.startswith("_"):
                    attr = getattr(module, name)
                    if isinstance(attr, types.FunctionType):
                        attr = self._run_on_failure_decorator(attr)
                        attr = self._xpath_decorator(attr)
                        setattr(self, name, attr)

    def _run_on_failure_decorator(self, keyword_method: Callable[..., Any]) -> Callable[..., None]:
        """Decorator method for keywords.

        If keyword fails then this method executes self.run_on_failure_keyword.
        """

        @wraps(keyword_method)  # Preserves docstring of the original method.
        def inner(*args: Any, **kwargs: Any) -> None:  # pylint: disable=R1710
            kwargs = {k.lower(): v for k, v in kwargs.items()}  # Kwargs keys to lowercase
            if 'type_secret' not in str(keyword_method):
                logger.debug('args: {}, kwargs: {}'.format(args, kwargs))
            try:
                time.sleep(_timestr_to_secs(kwargs.get('delay', CONFIG['Delay'])))
                run_before = CONFIG['RunBefore']
                valid_pw = ['click', 'get_text', 'drop_down']
                if run_before and any(pw in str(keyword_method) for pw in valid_pw):
                    logger.info('executing run before kw {}'.format(run_before))
                    # robot fw or python syntax
                    if isinstance(run_before, list):
                        BuiltIn().run_keyword(run_before[0], *run_before[1:])
                    elif util.is_py_func(run_before):
                        eval(run_before)  # pylint: disable=W0123
                    else:
                        BuiltIn().run_keyword(run_before)
                logger.trace(keyword_method)
                logger.trace(args, kwargs)
                return keyword_method(*args, **kwargs)
            except Exception as e:  # pylint: disable=W0703
                logger.debug(traceback.format_exc())
                if not self._is_run_on_failure_keyword(keyword_method):
                    if not util.par2bool(kwargs.get('skip_screenshot', False)):
                        try:
                            BuiltIn().run_keyword(self._run_on_failure_keyword)
                        except RobotNotRunningError:
                            logger.debug("Robot not running")
                devmode = util.par2bool(util.get_rfw_variable_value('${DEV_MODE}', False))
                if devmode and not config.get_config('Debug_Run'):
                    Dialogs.pause_execution('Keyword {} {} {} failed. \n'
                                            'Got {}'.format(
                                                str(keyword_method).split(' ')[1].upper(),
                                                str(args), str(kwargs), e))
                    debug.debug_on()
                else:
                    raise

        return inner

    @staticmethod
    def _xpath_decorator(keyword_method: Callable[..., Any]) -> Callable[..., Callable[..., Any]]:
        """Decorator method for selector-attribute. If selector attribute
        is given, method uses it's value and text to form simple xpath
        locator.
        """

        @wraps(keyword_method)  # Preserves docstring of the original method.
        def create_xpath(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            """Handle xpath before passing it to keyword.
            """
            args_list = list(args)
            if 'selector' in kwargs:
                attr_value = str(args_list[0])
                args_list[0] = '//*[@{}="{}"]'.format(kwargs['selector'], attr_value)
                del kwargs['selector']
                args = tuple(args_list)
            return keyword_method(*args, **kwargs)

        return create_xpath

    def _is_run_on_failure_keyword(self, method: Callable[..., Any]) -> bool:
        """Helper function to find out if method name is the
         one registered as kw to run on failure"""
        return self._run_on_failure_keyword.replace(" ", "_").lower() == method.__name__


# pylint: disable=wrong-import-position
from ._version import get_versions  # noqa: E402

__version__ = get_versions()['version']
del get_versions
