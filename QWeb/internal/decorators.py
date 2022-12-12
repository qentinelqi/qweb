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
from types import MappingProxyType
from typing import Callable, Any, Union

import time
from inspect import signature
from functools import wraps
from robot.utils import timestr_to_secs
from robot.api import logger
from selenium.common.exceptions import InvalidSelectorException, \
    NoSuchElementException, StaleElementReferenceException, WebDriverException, \
    UnexpectedAlertPresentException, InvalidSessionIdException
from QWeb.keywords import config
from QWeb.internal import frame
from QWeb.internal.config_defaults import CONFIG, SHORT_DELAY, LONG_DELAY
from QWeb.internal.exceptions import QWebElementNotFoundError, \
    QWebStalingElementError, QWebDriverError, QWebTimeoutError, QWebValueError, \
    QWebUnexpectedConditionError, QWebValueMismatchError, QWebSearchingMode, QWebUnexpectedAlert, \
    QWebIconNotFoundError, QWebBrowserError, FATAL_MESSAGES


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
def timeout_decorator(fn: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(fn)
    def get_elements_from_dom_content(  # type: ignore[return] # pylint: disable=R1710
            *args: Any, **kwargs: Any) -> Union[Callable[..., Any], int, bool, None]:
        try:
            args, kwargs, locator = _equal_sign_handler(args, kwargs, fn)
            msg: Union[WebDriverException, QWebDriverError, QWebValueError, None] = None
            params = signature(fn).parameters
            args, kwargs = _args_to_kwargs(params, args, kwargs)
            timeout = get_timeout(**kwargs)
            logger.debug('Timeout is {} sec'.format(timeout))

            try:
                if 'go_to' not in str(fn) and 'switch_window' not in str(fn):
                    frame.wait_page_loaded()
            except UnexpectedAlertPresentException as e:
                if not CONFIG["HandleAlerts"]:
                    raise QWebUnexpectedAlert(str(e)) from e
                logger.debug('Got {}. Trying to retry..'.format(e))
                time.sleep(SHORT_DELAY)
            start = time.time()
            while time.time() < timeout + start:
                try:
                    kwargs['timeout'] = float(timeout + start - time.time())
                    config.set_config('FrameTimeout', float(timeout + start - time.time()))
                    return fn(*args, **kwargs)
                except (QWebUnexpectedConditionError, QWebTimeoutError) as e:
                    logger.debug('Got {}'.format(e))
                except (InvalidSelectorException, NoSuchElementException, QWebElementNotFoundError,
                        UnexpectedAlertPresentException, QWebStalingElementError,
                        StaleElementReferenceException, QWebIconNotFoundError) as e:
                    time.sleep(SHORT_DELAY)
                    logger.debug('Got exception: {}. Trying to retry..'.format(e))
                except InvalidSessionIdException as e:
                    CONFIG.set_value("OSScreenshots", True)
                    raise QWebBrowserError("Browser session lost. Did browser crash?") from e
                except (WebDriverException, QWebDriverError) as e:
                    if any(s in str(e) for s in FATAL_MESSAGES):
                        CONFIG.set_value("OSScreenshots", True)
                        raise QWebBrowserError(e)  # pylint: disable=W0707
                    logger.debug('From timeout decorator: Webdriver exception. Retrying..')
                    logger.debug(e)
                    time.sleep(SHORT_DELAY)
                    err = QWebDriverError
                    msg = e
                except QWebValueError as ve:
                    logger.debug('Got QWebValueError: {}. Trying to retry..'.format(ve))
                    err = QWebValueError  # type: ignore[assignment]
                    msg = ve
                    time.sleep(SHORT_DELAY)
            if msg:
                raise err(msg)
            if 'count' in str(fn):
                return 0
            if 'is_text' in str(fn) or 'is_no_text' in str(fn):
                return False
            raise QWebElementNotFoundError('Unable to find element for locator {} in {} sec'.format(
                locator, timeout))
        except QWebSearchingMode:
            pass

    return get_elements_from_dom_content


def timeout_decorator_for_actions(fn: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(fn)
    def perform(*args: Any, **kwargs: Any) -> Callable[..., Any]:
        params = signature(fn).parameters
        args, kwargs = _args_to_kwargs(params, args, kwargs)
        timeout = get_timeout(**kwargs)
        err = None
        msg = None
        performed = False
        logger.debug('time to run {}'.format(timeout))
        start = time.time()
        while time.time() < timeout + start:
            try:
                return fn(*args, **kwargs)
            except QWebValueMismatchError as mismatch:
                if 'text_appearance' not in str(fn) and 'get_or_compare_text' not in str(fn):
                    err = QWebValueError
                    msg = mismatch
                logger.trace('Value mismatch: {}'.format(mismatch))
                continue
            except (QWebElementNotFoundError, UnexpectedAlertPresentException):
                logger.debug('Not found')
                time.sleep(SHORT_DELAY)
            except QWebValueError as ve:
                if performed:
                    break
                raise ve
            except (QWebStalingElementError, StaleElementReferenceException) as S:
                if 'execute_click' in str(fn) or 'text_appearance' in str(fn):
                    logger.debug('Got staling element err from retry click.'
                                 'Action is probably triggered.')
                    raise QWebUnexpectedConditionError(S)  # pylint: disable=W0707
                raise QWebStalingElementError('Staling element')  # pylint: disable=W0707
            except (WebDriverException, QWebDriverError) as wde:
                if 'alert' in str(fn):
                    time.sleep(LONG_DELAY)
                    logger.debug("Got webdriver exception..{}. Retrying..".format(wde))
                    err = QWebDriverError  # type: ignore[assignment]
                    msg = wde  # type: ignore[assignment]
                else:
                    raise QWebDriverError(wde)  # pylint: disable=W0707
        if msg:
            raise err(msg)  # type: ignore[misc]
        raise QWebTimeoutError('Timeout exceeded')

    return perform


def get_timeout(**kwargs: Any) -> Union[int, float]:
    timeout = timestr_to_secs(CONFIG["DefaultTimeout"])
    if 'timeout' in kwargs:
        if timestr_to_secs(kwargs['timeout']) != 0:
            timeout = timestr_to_secs(kwargs['timeout'])
    return timeout


def _args_to_kwargs(params: MappingProxyType[str, Any], args: tuple,
                    kwargs: dict) -> tuple[tuple, dict]:
    if 'timeout' not in kwargs:
        for i, p in enumerate(params.values()):
            if p.name not in kwargs:
                if len(args) > i:
                    kwargs[p.name] = args[i]
                else:
                    kwargs[p.name] = p.default
        args = tuple('')
    return tuple(args), kwargs


def _equal_sign_handler(args: Union[tuple, list], kwargs: dict,
                        function_name: Union[str, Callable[..., Any]]) -> tuple[tuple, dict, str]:
    try:
        locator = args[0]
    except IndexError:
        for key, value in kwargs.items():
            # if present any of these is always the first argument
            # locator can be the 2nd arg but it is handled later on
            if key in ('locator', 'xpath', 'steps', 'image', 'input_texts', 'input_values', 'text',
                       'coordinates', 'texts_to_verify', 'url', 'title'):
                locator = value
                break
        else:
            # index can be unnamed first argument or named argument
            locator = kwargs.get('index', None)

        # The only decorated method with 'locator' as NOT the first argument
        if str(function_name) == "scroll_to":
            locator = kwargs.get('text_to_find', None)

    if locator is None:
        logger.console(f"args: {args}, \nkwargs: {kwargs}")
        raise QWebElementNotFoundError("Use \\= instead of = in xpaths")
    return tuple(args), kwargs, locator
