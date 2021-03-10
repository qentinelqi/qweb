# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------
import time

from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

from QWeb.internal import element, frame, xhr
from QWeb import config


class SanomaWeb(object):
    def __init__(self):
        """Initialize library.

        Sets wait function for sanoma pages.

        Adds run on failure capability to keywords implemented by this class.
        """
        config.set_wait_function(self.wait_spinner)
        self.QWeb = BuiltIn().get_library_instance('QWeb')
        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name)
            if hasattr(attribute, "robot_name"):
                attribute = self.QWeb._run_on_failure_decorator(attribute)
                setattr(self, attribute_name, attribute)

    @keyword
    def click_header(self, text):
        """Click header text."""
        frame.wait_page_loaded()
        xpath = ('//ul/li/a[.="{}"]'.format(text))
        webelements = element.get_webelements_in_active_area(xpath)
        if not webelements:
            raise AssertionError('Could not find header with text {}'
                                 .format(text))
        elif len(webelements) == 1:
            webelements[0].click()
        else:
            raise AssertionError('Found {} occurences of headers with text {}'
                                 .format(len(webelements), text))

    def wait_spinner(self):
        """Wait until there is no longer spinner visible."""
        xhr.wait_xhr(10)
        time.sleep(0.2)
        timeout = 15
        start = time.time()
        xpath = '//img[@alt="Loading..."]'
        found = False
        while time.time() - start < timeout:
            try:
                webelements = element.get_webelements(xpath)
            except Exception:
                continue
            if webelements:
                if not found:
                    found = True
                    logger.info('Found spinner(s)')
            else:
                if found:
                    logger.info('No more spinners visible.')
                else:
                    logger.info('Page did not contain spinners.')
                xhr.wait_xhr(10)
                return
        raise AssertionError('Spinner was visible after {}s'.format(timeout))
