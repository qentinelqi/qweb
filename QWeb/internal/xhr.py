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
import time
from robot.api import logger
from selenium.common.exceptions import WebDriverException, JavascriptException
from QWeb.internal.exceptions import QWebDriverError
from QWeb.internal import javascript


def setup_xhr_monitor() -> bool:
    """Inject jQuery if needed and check if page is ready.

    Setup_xhr_monitor injects jQuery to page if there isn't one
    already.

    """
    try:
        js = """
        function inject(){
            if (typeof(jQuery) === "undefined"){
               var head = document.querySelector('head');
               var script = document.createElement('script');
               script.type = "text/javascript";
               script.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"
               head.appendChild(script);
               if (typeof(jQuery) === "undefined"){
                    return false;
               }
            }
            return true;
        }
        return inject()"""

        return javascript.execute_javascript(js)

    except (WebDriverException, JavascriptException) as e:
        raise QWebDriverError(e)  # pylint: disable=W0707


def get_ready_state() -> bool:
    ready_state = javascript.execute_javascript('return document.readyState === "complete"')
    logger.debug('Readystate = {}'.format(ready_state))
    return ready_state


def get_jquery_ready() -> bool:
    jqueries_ready = javascript.execute_javascript('return window.jQuery.active === 0;')
    return jqueries_ready


def wait_xhr(timeout: float = 0.0) -> None:
    """Uses jQuery.active to check if page is ready

    if jQuery is not available, calls setup_xhr_monitor
    which injects it to the page.
    jQuery.active returns 0 when page and js are ready and
    AJAX is done.

    """
    start = time.time()
    while time.time() < timeout + start:
        logger.debug('Timeout for xhr:s = {}'.format(timeout))
        ready_state = get_ready_state()
        logger.debug("ready_state {}".format(ready_state))
        if ready_state:
            jquery = setup_xhr_monitor()
            if jquery:
                jquery_ready = get_jquery_ready()
                if jquery_ready:
                    return
                logger.debug('There are still pending AJAX requests..')
            else:
                logger.debug('Unable to inject jQuery..')
                return
        else:
            logger.debug('Page is not loaded yet..')

    logger.debug('Page was not ready after {} seconds.'
                 'Trying to continue..'.format(timeout))
