# -*- coding: utf-8 -*-rf
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
from typing import Optional, Any, Callable, Union
import os
import pyperclip
from pyautogui import KEY_NAMES
from robot.api import logger
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException
from QWeb.internal.exceptions import QWebInvalidElementStateError, QWebValueError, \
    QWebEnvironmentError
from QWeb.internal import javascript

try:
    if not os.getenv('QWEB_HEADLESS', None):
        from pynput.keyboard import Controller
except ImportError:
    logger.warn('Cannot import pynput.keyboard, no display detected')


class InputHandler:

    def __init__(self,
                 input_method: str = "selenium",
                 line_break_key: str = "\ue004",
                 clear_key: Optional[str] = None) -> None:
        self._input_method = input_method
        self.line_break_key = line_break_key
        self.clear_key = clear_key

    @property
    def input_method(self) -> str:
        return self._input_method

    @input_method.setter
    def input_method(self, input_method: str) -> None:
        required = ["javascript", "selenium", "raw"]
        if input_method not in required:
            raise QWebValueError('Unknown input_method: {}, required: {}'.format(
                input_method, required))
        self._input_method = input_method

    def write(self, input_element: WebElement, input_text: str, **kwargs) -> None:
        """ Writes the given text using configured writer. """
        write = self._get_writer()
        # By clearing the input field with Javascript,
        # we avoid triggering focus events right after
        # clear and trigger them only on send_keys call.
        clear_key = self.check_key(kwargs.get('clear_key', self.clear_key))
        shadow_dom = kwargs.get('shadow_dom', False)
        if not clear_key:
            if self.is_editable_text_element(input_element):
                javascript.execute_javascript('arguments[0].innerText=""', input_element)
            else:
                javascript.execute_javascript("arguments[0].value = \"\"", input_element)
        else:
            input_element.send_keys(clear_key)
        try:
            write(input_element, input_text)
        # workaround for Firefox shadow dom inputs not always being reachable
        except ElementNotInteractableException as e:
            if shadow_dom:
                javascript.execute_javascript(f'arguments[0].value = "{input_text}"', input_element)
                kwargs['key'] = None
            else:
                raise e from e

        if 'check' not in kwargs:
            line_break = kwargs.get('key', self.check_key(self.line_break_key))
            if line_break:
                input_element.send_keys(line_break)

    def _get_writer(self) -> Callable[..., Any]:
        if self._input_method == "selenium":
            return InputHandler._selenium_writer
        if self._input_method == "javascript":
            return InputHandler._js_writer
        return self._raw_writer

    @staticmethod
    def _selenium_writer(input_element: WebElement, input_text: str) -> None:
        """ Use Selenium librarys input methods clear() and send_keys(). """
        if not input_element.is_enabled():
            logger.warn("Element not enabled. Try with alternative input method?")
            raise QWebInvalidElementStateError("Input element is not enabled")
        input_element.send_keys(input_text)

    @staticmethod
    def _js_writer(input_element: WebElement, input_text: str) -> None:
        """ Use JavaScript to set input element value."""
        if not input_element.is_enabled():
            logger.warn("Element not enabled. Try with alternative input method?")
            raise QWebInvalidElementStateError("Input element is not enabled")
        javascript.execute_javascript(f'arguments[0].value = "{input_text}"', input_element)

    @staticmethod
    def _raw_writer(input_element: WebElement, input_text: str) -> None:
        """ Control keyboard and text input with pyautogui. This doesn't
            do any checks for the element state.
        """
        # Sanity check even if the input_element is not required for the input
        if not input_element:
            raise QWebValueError('Input element is not available.')
        if os.getenv('QWEB_HEADLESS', None):
            raise QWebEnvironmentError('Running in headless environment. Pynput is unavailable.')
        keyboard = Controller()
        keyboard.type(input_text)

    @staticmethod
    def is_editable_text_element(input_element: WebElement) -> bool:
        if javascript.execute_javascript(
                'return arguments[0].getAttribute("contenteditable") == "true"', input_element):
            return True
        return False

    @staticmethod
    def check_key(key: Optional[str]) -> Union[Optional[str], list[Optional[str]]]:
        if not key:
            return None
        if key == '{PASTE}':
            return pyperclip.paste()
        hotkey = []
        if key.startswith('{') and key.endswith('}'):
            key = key[1:-1].upper()
            if '+' in key:
                keys = key.split('+')
                for k in keys:
                    try:
                        key = getattr(Keys, k.strip())
                    except AttributeError:
                        key = k.lower().strip()
                    hotkey.append(key)
                return hotkey
            key = getattr(Keys, key)
        return key

    @staticmethod
    def check_key_pyautogui(key: Optional[str]) -> Union[Optional[str], list[str]]:
        if not key:
            return None
        if key == '{PASTE}':
            return pyperclip.paste()
        hotkey = []
        if key.startswith('{') and key.endswith('}'):
            key = key[1:-1].lower()
            if '+' in key:
                keys = key.split('+')
                for k in keys:
                    if not k.strip() in KEY_NAMES:
                        raise AttributeError
                    key = k.strip()
                    hotkey.append(key)
                return hotkey
            if not key.strip() in KEY_NAMES:
                raise AttributeError
        return key


# Instantiate here as global
INPUT_HANDLER: InputHandler = InputHandler()
