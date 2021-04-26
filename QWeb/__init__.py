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

import traceback
import types
import time

from functools import wraps
import QWeb.config as custom_config
from QWeb.keywords import (alert, browser, window, frame, element, text, checkbox,
                           input_, javascript, screenshot, download, table,
                           search_strategy, dropdown, cookies, config, icon,
                           dragdrop, lists, file, debug, ajax, blocks)

from QWeb.internal import util
from QWeb.internal.config_defaults import CONFIG
from robot.api import logger
from robot.utils import timestr_to_secs
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries import Dialogs


class QWeb:

    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self, run_on_failure_keyword="Log Screenshot"):
        """Adds all the keywords to the instance."""
        self._run_on_failure_keyword = run_on_failure_keyword
        for module in (alert, browser, window, frame, element, text, checkbox, input_,
                       javascript, screenshot, custom_config, download, search_strategy, table,
                       dropdown, cookies, config, icon, dragdrop, lists, file, debug, ajax, blocks):
            for name in dir(module):
                if not name.startswith("_"):
                    attr = getattr(module, name)
                    if isinstance(attr, types.FunctionType):
                        attr = self.run_on_failure_decorator(attr)
                        attr = self.xpath_decorator(attr)
                        setattr(self, name, attr)

    def run_on_failure_decorator(self, keyword_method):
        """Decorator method for keywords.

        If keyword fails then this method executes self.run_on_failure_keyword.
        """
        @wraps(keyword_method)  # Preserves docstring of the original method.
        def inner(*args, **kwargs):
            kwargs = {k.lower(): v for k, v in kwargs.items()}  # Kwargs keys to lowercase
            if 'type_secret' not in str(keyword_method):
                logger.debug('args: {}, kwargs: {}'.format(args, kwargs))
            try:
                time.sleep(timestr_to_secs(kwargs.get('delay', CONFIG['Delay'])))
                run_before_kw = CONFIG['RunBefore']
                valid_pw = ['click', 'get_text', 'drop_down']
                if run_before_kw and any(pw in str(keyword_method) for pw in valid_pw):
                    logger.info('executing run before kw {}'.format(run_before_kw))
                    eval(run_before_kw)  # pylint: disable=W0123
                logger.trace(keyword_method)
                logger.trace(args, kwargs)
                return keyword_method(*args, **kwargs)
            except Exception as e:  # pylint: disable=W0703
                logger.debug(traceback.format_exc())
                if not self._is_run_on_failure_keyword(keyword_method):
                    if not util.par2bool(kwargs.get('skip_screenshot', False)):
                        BuiltIn().run_keyword(self._run_on_failure_keyword)
                devmode = util.par2bool(BuiltIn().get_variable_value('${DEV_MODE}', False))
                if devmode and not config.get_config('Debug_Run'):
                    Dialogs.pause_execution(
                        'Keyword {} {} {} failed. \n'
                        'Got {}'.format(str(keyword_method).split(' ')[1].upper(),
                                        str(args), str(kwargs), e))
                    debug.debug_on()
                else:
                    raise
        return inner

    @staticmethod
    def xpath_decorator(keyword_method):
        """Decorator method for selector-attribute. If selector attribute
        is given, method uses it's value and text to form simple xpath
        locator.
        """
        @wraps(keyword_method)  # Preserves docstring of the original method.
        def create_xpath(*args, **kwargs):
            """Handle xpath before passing it to keyword.
            """
            args_list = list(args)
            if 'selector' in kwargs:
                attr_value = str(args_list[0])
                args_list[0] = '//*[@{}="{}"]'.format(kwargs['selector'], attr_value)
                del kwargs['selector']
                args = args_list
            return keyword_method(*args, **kwargs)
        return create_xpath

    def _is_run_on_failure_keyword(self, method):
        """Helper function to find out if method name is the
         one registered as kw to run on failure"""
        return self._run_on_failure_keyword.replace(
            " ", "_").lower() == method.__name__


# pylint: disable=wrong-import-position
from ._version import get_versions  # noqa: E402
__version__ = get_versions()['version']
del get_versions
