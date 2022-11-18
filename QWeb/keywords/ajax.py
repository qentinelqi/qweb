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
from typing import Union, Optional

from QWeb.internal import decorators, ajax, util
from robot.api.deco import keyword


@keyword(tags=["Logging"])
@decorators.timeout_decorator
def save_file(
        locator: str,
        filename: Optional[str] = None,
        anchor: str = "1",
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        path: Optional[str] = None,
        **kwargs) -> None:
    r"""Save file using http-request.

    Needs url of the downloadable content which usually is in element's href attribute.
    Text or tooltip can be used as a locator (Works as ClickText or ClickItem).
    If locator element is not the one with href-attribute, tries to get href from closest
    parent with <a> tag in it.

    url can be used as a locator too.

    Available element types without using tag attribute:
    *a, span, img, li, h1, h2, h3, h4, h5, h6, div, svg, p, button, input\*
    (\*submit buttons only).*

    Examples
    --------
    .. code-block:: robotframework

        SaveFile      ClickMe       filename.pdf
        SaveFile      tooltip       filename.xml

        # Locators parent or child element is the one with href:
        SaveFile      ClickMe       filename.pdf    child=a
        SaveFile      tooltip       filename.xml    parent=div

        # Create folder for downloadable files:
        SaveFile      ClickMe       pdf/filename.pdf
        SaveFile      tooltip       xml/filename.xml
        SaveFile      Robot         pics/filename.png

        # Using url as locator
        SaveFile      https://www.robot.fi/robot.xml  filename.xml

        # Get html content of given url
        SaveFile      https://www.qentinel.com      qentinel.html

    Parameters
    ----------
    locator : str
        Text or item to be "clicked".
    filename: str
        Wanted filename
    anchor : str
        Text near the element to be clicked or index. If the page contains many
        places where the text argument is then anchor is used to get the
        one that is closest to it.  (default 1)
    timeout : str | int
        How long we wait for element to be ready for click
    path : str
        Wanted path for files. Default path is users download folder.
    kwargs :
        |  Accepted kwargs:
        |       tag : html tag of preferred element -
        |           If tag is used then element is found
        |           by some of it's attribute
        |       parent : str: tag name for clickable parent
        |       child : str: tag name for clickable child.
        |       index : str: use index if there is multiple
        |       childs with same tag name
        |       headers : dict -Pass headers to http request

    Related keywords
    ----------------
    \`ExpectFileDownload\`, \`UploadFile\`, \`UseFile\`,
    \`VerifyFile\`, \`VerifyFileDownload\`
    """
    if locator.startswith('http'):
        url = locator
    else:
        url = ajax.get_url_for_http_request(locator, anchor, **kwargs)
    response = ajax.http_request_with_browser_cookies(url)
    if not filename:
        filename = str(
            util.get_substring(
                response.headers.get(
                    'Content-Disposition',
                    'filename=unnamed.{}'.format(
                        response.headers.get(  # type: ignore[union-attr]
                            'Content-Type').split('/')[1].split(';')[0])),
                between='filename=???'))
    ajax.save_response_as_file(response, str(filename), path)
