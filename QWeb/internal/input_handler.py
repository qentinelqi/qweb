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


import os
import pyperclip
from robot.api import logger
from selenium.webdriver.common.keys import Keys
from QWeb.internal.exceptions import QWebInvalidElementStateError, QWebValueError,\
    QWebEnvironmentError
from QWeb.internal import javascript


try:
    if not os.getenv('QWEB_HEADLESS', None):
        from pynput.keyboard import Controller
except ImportError:
    logger.warn('Cannot import pynput.keyboard, no display detected')


class InputHandler:
    def __init__(self, input_method="selenium", line_break_key="\ue004", clear_key=None):
        self._input_method = input_method
        self.line_break_key = line_break_key
        self.clear_key = clear_key

    @property
    def input_method(self):
        return self._input_method

    @input_method.setter
    def input_method(self, input_method):
        required = ["selenium", "raw"]
        if input_method not in required:
            raise QWebValueError('Unknown input_method: {}, required: {}'
                                 .format(input_method, required))
        self._input_method = input_method

    def write(self, input_element, input_text, **kwargs):
        """ Writes the given text using configured writer. """
        write = self._get_writer()
        # By clearing the input field with Javascript,
        # we avoid triggering focus events right after
        # clear and trigger them only on send_keys call.
        clear_key = self.check_key(kwargs.get('clear_key', self.clear_key))
        if not clear_key:
            if self.is_editable_text_element(input_element):
                javascript.execute_javascript('arguments[0].innerText=""', input_element)
            else:
                javascript.execute_javascript("arguments[0].value = \"\"", input_element)
        else:
            input_element.send_keys(clear_key)
        write(input_element, input_text)
        if 'check' not in kwargs:
            line_break = kwargs.get('key', self.check_key(self.line_break_key))
            if line_break:
                input_element.send_keys(line_break)

    def _get_writer(self):
        if self._input_method == "selenium":
            return InputHandler._selenium_writer
        return self._raw_writer

    @staticmethod
    def _selenium_writer(input_element, input_text):
        """ Use Selenium librarys input methods clear() and send_keys(). """
        if not input_element.is_enabled():
            logger.warn("Element not enabled. Try with alternative input method?")
            raise QWebInvalidElementStateError("Input element is not enabled")
        input_element.send_keys(input_text)

    @staticmethod
    def _raw_writer(input_element, input_text):
        """ Control keyboard and text input with pyautogui. This doesn't
            do any checks for the element state.
        """
        # Sanity check even if the input_element is not required for the input
        if not input_element:
            raise QWebValueError('Input element is not available.')
        if os.getenv('QWEB_HEADLESS', None):
            raise QWebEnvironmentError(
                'Running in headless environment. Pynput is unavailable.')
        keyboard = Controller()
        keyboard.type(input_text)

    @staticmethod
    def is_editable_text_element(input_element):
        if javascript.execute_javascript(
                'return arguments[0].getAttribute("contenteditable") == "true"',
                input_element):
            return True
        return False

    @staticmethod
    def check_key(key):
        if not key:
            return None
        if key == '{PASTE}':
            return pyperclip.paste()
        hotkey = ""
        if key.startswith('{') and key.endswith('}'):
            key = key[1:-1].upper()
            if '+' in key:
                keys = key.split('+')
                for k in keys:
                    try:
                        key = getattr(Keys, k.strip())
                    except AttributeError:
                        key = k.lower().strip()
                    hotkey += key
                return hotkey
            key = getattr(Keys, key)
        return key


# Instantiate here as global
INPUT_HANDLER = InputHandler()
