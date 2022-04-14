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
from typing import Optional, Any
from requests import Response

import os
import requests
from pathlib import Path
from QWeb.internal.exceptions import QWebValueError, QWebElementNotFoundError
from QWeb.internal import download, text, browser, element
from QWeb.internal import javascript as js
from robot.api import logger


def http_request_with_browser_cookies(url: str,
                                      headers: Optional[dict[str, Any]] = None) -> Response:
    """ Copy cookies from current browser session
        and use them with request session
    """
    driver = browser.get_current_browser()
    if not headers:
        headers = {'User-Agent': '{}'.format(js.execute_javascript('return navigator.userAgent'))}
    cookies = driver.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    return s.get(url, headers=headers)


def get_url_for_http_request(locator: str, anchor: str, **kwargs: Any) -> str:
    """ Get href-attribute (=url) from found web element.
    """
    script = """
       var href = function(el) {
               if (el.hasAttribute("href")) {
                   return el.href;
                   console.log(el.attributes["href"].value);
               }
               return arguments[0].closest("a").href;
           }
           return href(arguments[0]);
       """
    index = int(kwargs.get('index', 1) - 1)
    try:
        elem = text.get_item_using_anchor(locator, anchor, **kwargs)
    except QWebElementNotFoundError:
        elem = None
    if not elem:
        elem = text.get_text_using_anchor(locator, anchor, **kwargs)
    if kwargs.get('parent', None):
        elem = element.get_parent_element(elem, str(kwargs.get('parent')))
    if kwargs.get('child', None):
        elem = element.get_element_from_childnodes(elem,
                                                   str(kwargs.get('child')),
                                                   dom_traversing=False)[index]
    url = js.execute_javascript(script, elem)
    if url:
        return url
    raise QWebValueError('Unable to find valid url for locator {}'.format(locator))


def save_response_as_file(response: Response,
                          filename: str,
                          root_path: Optional[str] = None) -> None:
    if root_path is None:
        path = download.get_downloads_dir()
    else:
        path = root_path

    logger.debug('path before {}'.format(path))
    if '/' in filename:
        folders = filename.split('/')
        for i in range(len(folders) - 1):
            logger.debug(folders[i])
            if not Path(os.path.join(path, folders[i])).exists():
                os.makedirs(os.path.join(path, folders[i]))
            path = os.path.join(path, folders[i])
        real_path = Path(path) / folders[len(folders) - 1]
    else:
        real_path = Path(path) / filename
    logger.info('path is {}'.format(path))
    with open(real_path, 'wb') as file:
        file.write(response.content)
