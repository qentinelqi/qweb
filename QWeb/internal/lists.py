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

from robot.api import logger
from QWeb.internal.exceptions import QWebElementNotFoundError
from QWeb.internal import element, text, javascript, frame
from QWeb.internal.config_defaults import CONFIG


class List:

    ACTIVE_LIST = None

    def __init__(
            self, web_list, web_element_list, locator, anchor, parent=None, child=None, **kwargs):
        self.web_list = web_list
        self.web_element_list = web_element_list
        self.locator = locator
        self.anchor = anchor
        self.parent = parent
        self.child = child
        self.kwargs = kwargs
        List.ACTIVE_LIST = self

    @classmethod
    @frame.all_frames
    def from_list_instance(cls, locator, anchor="1", parent=None, child=None, **kwargs):
        """Find list and create list instance

        Parameters
        ----------
        locator : str
            Text that locates the table. The table that is closest
            to the text is selected. Also one can use xpath by adding xpath= prefix
            and then the xpath. Error is raised if the xpath matches to multiple
            elements.
        anchor : str
            Text near the table's locator element. If the page contains
            many places where the locator is then anchor is used to get the
            one that is closest to it.
        kwargs:
            tag : html_tag
                When finding list by text which is inside of it use tag to point
                out wanted parent element.
                For example ul, ol etc. if parameter is not given, uses default = UL.
        """
        web_list, web_element_list = cls.create_list(
            cls, locator, anchor, parent=parent, child=child, **kwargs)
        return List(web_list, web_element_list, locator, anchor, parent, child, **kwargs)

    def create_list(self, locator, anchor, **kwargs):
        if locator.startswith('//') or locator.startswith('xpath='):
            if locator.startswith('xpath='):
                locator = locator.split("=", 1)[1]
            web_elements = self.get_elements_by_locator_xpath_and_tag_name(
                locator, anchor, **kwargs)
        else:
            web_elements = self.get_elements_by_locator_text_and_tag_name(locator, anchor, **kwargs)
            logger.debug('webelems: {}'.format(web_elements))
        if web_elements:
            if CONFIG['SearchMode']:
                element.draw_borders(web_elements)
            web_list = self.get_texts(web_elements)
            return web_list, web_elements
        raise QWebElementNotFoundError('Suitable elements not found')

    @staticmethod
    def get_elements_by_locator_text_and_tag_name(locator, anchor, index=1, **kwargs):
        index = int(index) - 1
        if 'tag' in kwargs:
            tag_name = kwargs.get('tag')
        elif 'parent' in kwargs and kwargs['parent']:
            tag_name = kwargs['parent']
        elif 'child' in kwargs and kwargs['child']:
            tag_name = kwargs['child']
        else:
            tag_name = 'ul'

        web_element = text.get_element_by_locator_text(locator, anchor)
        if 'parent' in kwargs and kwargs['parent']:
            tag = kwargs['parent']
            locator_element = element.get_parent_list_element(
                web_element, tag)
        elif 'child' in kwargs and kwargs['child']:
            tag = kwargs['child']
            locator_element = element.get_element_from_childnodes(
                web_element, tag, dom_traversing=False)[index]
            if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
                return locator_element
        else:
            locator_element = text.get_element_by_locator_text(locator, anchor)

        if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
            web_elements = javascript.execute_javascript(
                'return arguments[0].querySelectorAll("{}")'
                .format(tag_name), locator_element)
        else:
            web_elements = javascript.execute_javascript(
                'return arguments[0].closest("{}").querySelectorAll("li, dt, dd")'
                .format(tag_name), locator_element)
        return web_elements

    @staticmethod
    def get_elements_by_locator_xpath_and_tag_name(locator, index=1, **kwargs):
        index = int(index) - 1
        if 'tag' in kwargs:
            tag_name = kwargs.get('tag')
        elif 'parent' in kwargs and kwargs['parent']:
            tag_name = kwargs['parent']
        elif 'child' in kwargs and kwargs['child']:
            tag_name = kwargs['child']
        else:
            tag_name = 'ul'
        if 'parent' in kwargs and kwargs['parent']:
            web_element = element.get_unique_element_by_xpath(locator)
            css = kwargs.get('parent')
            web_element = element.get_parent_list_element(web_element, css)
            if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
                web_element = javascript.execute_javascript(
                    'return arguments[0].querySelectorAll("{}")'
                    .format(tag_name), web_element)
            else:
                web_element = javascript.execute_javascript(
                    'return arguments[0].closest("{}").querySelectorAll("li, dt, dd")'
                    .format(tag_name), web_element)
        elif 'child' in kwargs and kwargs['child']:
            web_element = element.get_unique_element_by_xpath(locator)
            css = kwargs.get('child')
            web_element = element.get_element_from_childnodes(
                web_element, css, dom_traversing=False)[index]
            if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
                web_element = javascript.execute_javascript(
                    'return arguments[0].querySelectorAll("{}")'
                    .format(tag_name), web_element)
            else:
                web_element = javascript.execute_javascript(
                    'return arguments[0].closest("{}").querySelectorAll("li, dt, dd")'
                    .format(tag_name), web_element)
        else:
            web_element = element.get_webelements_in_active_area(locator)

        return web_element

    @staticmethod
    def get_texts(web_elements):
        texts = []
        if isinstance(web_elements, list):
            for elem in web_elements:
                texts.append(elem.text)
        else:
            texts.append(web_elements.text)
        return texts

    def contains(self, expected_match, index):
        if index is None:
            if expected_match in self.web_list:
                return True
        else:
            if expected_match in str(self.web_list[index]).replace('\n', '').strip():
                return True
        return False

    def update_list(self):
        active_list = self.from_list_instance(
            self.locator, self.anchor, self.parent, self.child, **self.kwargs)
        return active_list
