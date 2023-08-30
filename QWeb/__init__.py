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

    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self, run_on_failure_keyword: str = "Log Screenshot") -> None:
        """Adds all the keywords to the instance."""
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
