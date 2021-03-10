# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2019 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
import decorators
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from QWeb.internal import javascript


class CustomerLib():
    def __init__(self):
        self.QWeb = BuiltIn().get_library_instance(u'QWeb')

    @keyword
    @decorators.log_screenshot
    def get_texts(self, locator):
        """Return texts that are containing locator.

    Examples
    --------
    .. code-block:: robotframework

        GetTexts          ITEM-

    Parameters
    ----------
    locator : str
       Text that we are searching for

    Returns
    -------
    list : List of found texts
        """
        js = """var web_elements = function(locator){
                    var matches = [];
                    var text = "";
                    var elems = document.querySelectorAll('button, a');
                    for (var i = 0; i < elems.length; i++) {
                        if(elems[i].tagName.toLowerCase() === 'input'){
                            text = elems[i].value;
                        }
                        else {
                            text = elems[i].innerText;
                        }
                        if (text.trim().includes(locator)){
                            matches.push(elems[i]);
                        }
                    }
                    return matches;
                }
                return(web_elements('""" + locator.replace("\'", "\\'") + """'));"""
        text_elements = javascript.execute_javascript(js)
        texts = list()
        for e in text_elements:
            texts.append(e.text)
            self.QWeb.verify_text(e.text)
        logger.debug('Found texts: {}'.format(texts))
        return texts
