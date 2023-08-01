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
from typing import Any, Union
from selenium.webdriver.remote.webelement import WebElement

from QWeb.internal import browser


def execute_javascript(script: str, *args) -> Any:
    """Run given javascript on current window.

    Parameters
    ----------
    script : str
        Javascript code.
    *args : WebElement
        WebElement object that is stored in to variable "arguments" which is
        an array in javascript. Check example.

    Returns
    -------
    str
        Output of the executed javascript.

    Example
    -------
    execute_javascript('arguments[0].setAttribute("style", "background-color:yellow")', web_element)
    """
    driver = browser.get_current_browser()
    return driver.execute_script(script, *args)


def get_visibility(web_elements: list[WebElement]) -> list[dict]:
    """Return web element objects.

    Object contains element itself, offset-status,
    css display & visibility properties + if element is
    in current viewport.(elem, viewport, css, offset).
    """

    js = """
        var visibility = function (elems) {
        var elemObjects = [];
        for (var i = 0; i < elems.length; i++) {
            var obj = {}
            var rects = elems[i].getBoundingClientRect();
            var obj = {
                elem: elems[i],
                viewport: rects.top >= 0 && rects.top < window.innerHeight \
                    && rects.left >= 0 && rects.left < window.innerWidth,
                css: getComputedStyle(elems[i]).display !== "none" \
                && getComputedStyle(elems[i]).visibility !== "hidden",
                offset: elems[i].offsetWidth > 0 || rects.width > 0
            };
            elemObjects.push(obj);
        }
        return elemObjects;
        }
        return(visibility(arguments[0]));
        """
    return execute_javascript(js, web_elements)


def highlight_element(element: WebElement,
                      draw_only: bool,
                      flash_border: bool = False,
                      color: str = "blue") -> None:
    """Highlight borders for given web element.

    Parameters
    ----------
    element : web element
        Element to highlight.
    draw_only : bool
        True = draw only, False = blink (2sec)
    flash_border : bool
        Flash 0.3s.
    color : str
        Border color (default: blue)
    """
    js = """
           function blink(el, style) {
               el.style.border = "5px solid {COLOR}";
               setTimeout(function(){
                   el.style.border = style;
               }, 2000);
           }

           function flash(el, style) {
               el.style.border = "5px solid {COLOR}";
                   setTimeout(function(){
                   el.style.border = style;
                   }, 300);
           }

           function show(el, draw_only, flash_border=false) {
               style = el.style.border;
               if (draw_only === false && flash_border === false) {
                   blink(el, style);
               }

               else if (flash_border === true && draw_only === false) {
                 flash(el, style)
               }

               else {
                   blink(el, "5px solid {COLOR}");
               }
           }

           show(arguments[0], arguments[1], arguments[2], arguments[3]);
           """
    js = js.replace("{COLOR}", color)
    execute_javascript(js, element, draw_only, flash_border, color)


def get_by_attributes(elements: list[WebElement], locator: str,
                      partial_match: bool) -> dict[str, list[WebElement]]:
    """Return web element by it's attribute value.

    Parameters
    ----------
    elements : web elements
        List of web elements.
    locator : str
        Attribute we are looking for, that some of the elements on the list may or may not contain.
        E. g: '[checked = true]'
    partial_match : bool
        If True we don't need a perfect match -> Full = ull.

    Returns
    -------
    obj
        Object including lists of full and partial matches.

    """

    js = """
        var web_elements = function(elems, locator, partial){
            var matches = [];
            var full = [];
            var part = [];
            for (var i = 0; i < elems.length; i++) {
               var attrs = elems[i].attributes;
               if (attrs == null){
                continue;
               }
               for (var j = 0; j < attrs.length; j++) {
                    if (attrs[j].value.trim() == locator) {
                        full.push(elems[i]);
                        break;
                    }
                    else if (partial && attrs[j].value.includes(locator)){
                        part.push(elems[i]);
                        break;
                    }
               }
            }
            matches = {full:full, partial:part};
            return matches;
        }
        return(web_elements(arguments[0], arguments[1], arguments[2]));"""
    return execute_javascript(js, elements, locator.replace("\'", "\\'"), partial_match)


def get_all_elements(css: str) -> list[WebElement]:
    """Return all web elements for given css-locator.
    Parameters
    ----------
    css : selector
        For example: p,h1,h2,h3,input

    Returns
    -------
    list of web elements.
    """
    return execute_javascript("return document.querySelectorAll('{}')".format(css))


def get_childnodes(locator_element: WebElement,
                   css: str,
                   level: int = 3,
                   traverse: bool = True) -> list[WebElement]:
    """Find matching childs for given locator element.
    Parameters
    ----------
    locator_element : web element
    css : css selector/html tag
        For example: input
    level : Traverse limit (how many steps we are going up while searching).
    traverse : bool
        If false, we are looking matches under locator element only.

    Returns
    -------
    list of web elements.
    """

    js = """
        var elements = function(locator, selector, level, traverse) {
            if (locator.querySelectorAll(selector).length > 0) {
                return locator.querySelectorAll(selector);
            }
            else if (traverse)
            {
                for (var i = 0; i < level; i++){
                    locator = locator.parentNode;
                    if (locator.querySelectorAll(selector).length > 0)
                        return locator.querySelectorAll(selector);
                }
            }
                return [];
            }
        return(elements(arguments[0], arguments[1],  arguments[2], arguments[3]));
        """
    return execute_javascript(js, locator_element, css, level, traverse)


def get_by_label(locator_text: str, css: str, level: int,
                 partial_match: bool) -> dict[str, list[WebElement]]:
    """Find element based on it's label.

    First we sneak if there is for-attribute available. If so, it's used
    to locate correct element. If for-attribute is not available then we are doing
    some dom-traversing to locate correct element.

    Parameters
    ----------
    locator_text : str
    css : css selector/html tag
        For example: input
    level : Traverse limit (how many steps we are going up while searching).
    partial_match : bool
        If True we don't need a perfect match -> Full = ull.

    Returns
    -------
    Object containing lists of full and partially matched elements.
    """

    js = """
        var traverse = function(locator, selector, level) {
            if (locator.querySelectorAll(selector).length > 0) {
                return locator.querySelectorAll(selector);
            }
            else
            {
                for (var i = 0; i < level; i++) {
                    locator = locator.parentNode;
                    if (locator.querySelectorAll(selector).length > 0)
                        return locator.querySelectorAll(selector);
                }
            }
            return [];
        }

        var get_by_for = function(needle, haystack) {
            for (var i = 0; i < haystack.length; i++) {
                if (haystack[i].hasAttribute('id') && haystack[i].getAttribute('id') == needle) {
                    return haystack[i];
                }
                if (haystack[i].hasAttribute('name') && haystack[i].getAttribute('name') == needle) {
                    return haystack[i];
                }
            }
            return null;
        }

        var web_elements = function(locator, selector, level, partial){
            var elems = document.querySelectorAll('label');
            var haystack = document.querySelectorAll(selector);
            var matches = [];
            var full_matches = [];
            var part_with_for = [];
            var part_matches = [];
            for (var i = 0; i < elems.length; i++) {
                if (elems[i].hasAttribute('for') && elems[i].innerText.trim() === locator) {
                    needle = elems[i].getAttribute('for');
                    target = get_by_for(needle, haystack);
                    if (target) {
                        full_matches.push(target);
                        continue;
                    }
                }
                else if (elems[i].innerText.trim() === locator) {
                    target = traverse(elems[i], selector, level)[0];
                    if(target)
                    {
                        full_matches.push(target);
                        continue;
                    }
                }
                if (partial === true) {
                    if (elems[i].hasAttribute('for') && elems[i].innerText.trim().includes(locator)) {
                        needle = elems[i].getAttribute('for');
                        target = get_by_for(needle, haystack);
                        if (target) {
                            part_with_for.push(target);
                            continue;
                        }
                    }
                    else if (elems[i].innerText.trim().includes(locator))
                    {
                        target = traverse(elems[i], selector, level)[0];
                        if(target)
                        {
                            part_matches.push(target);
                        }
                    }
                }
            }
            matches = {full:full_matches.concat(part_with_for), partial:part_matches};
            return matches;
        }
        return(web_elements(arguments[0], arguments[1], arguments[2], arguments[3]));
        """
    return execute_javascript(js, locator_text.replace("\'", "\\'"), css, level, partial_match)


def get_parent_list(locator_element: Union[WebElement, str], css: str
                    ) -> Union[WebElement, list[WebElement]]:
    """Get parent list for web element.

    Parameters
    ----------
    locator_element : str
    css : css selector/html tag
        For example: div

    Returns
    -------
    Object containing lists of full and partially matched elements.
    """
    js = """
        var element = function(locator, css) {
            let = list_tags = ["ul", "ol", "dl", "UL", "OL", "DL"]
            if (list_tags.includes(css)){
                if ((locator.parentNode.tagName === "UL" || locator.parentNode.tagName === "OL" || locator.parentNode.tagName === "DL") && locator.parentNode.parentNode.tagName === css.toUpperCase()) {
                    return locator.parentNode.parentNode
                }
                else if (locator.parentNode.parentNode.parentNode.tagName === css.toUpperCase()) {
                    return locator.parentNode.parentNode.parentNode
                }
            }
            else {
                return locator.parentNode.parentNode
            }
            return []
        }
        return(element(arguments[0], arguments[1]))
        """
    return execute_javascript(js, locator_element, css)


def find_text_from_textnodes(text: str, **kwargs) -> list[WebElement]:
    """Get parent list for web element.

    Parameters
    ----------
    text : str

    Returns
    -------
    List of web_elements (If textContent of element matches to preferred text).
    """
    js = """
        function getTextNodes(text, tag, partial) {
            let mainDoc = document.querySelector(tag)
            const iterator = document.createNodeIterator(mainDoc, NodeFilter.SHOW_TEXT);
            const textNodes = [];
            let currentNode;
            while ((currentNode = iterator.nextNode())) {
                if(currentNode.textContent.trim() === text){
                    textNodes.push(currentNode.parentElement);
                    continue;
                }
                else if (partial && currentNode.textContent.trim().includes(text)) {
                    textNodes.push(currentNode.parentElement);
                }
            }
            return textNodes;
        }
        return(getTextNodes(arguments[0], arguments[1], arguments[2]))
        """
    doc = 'html'
    partial = kwargs.get('partial_match')
    return execute_javascript(js, text, doc, partial)


def get_clickable(locator: str) -> list[WebElement]:
    js = """
    var web_elements = function(locator){
        var full = [];
        var partial = [];
        var candidates = [];
        var text = "";
        var elems = document.querySelectorAll('button, a, label,\
        *[type="submit"], *[type="button"], *[type="reset"], li[data-value], input[type="radio"],\
        *[role="tab"], *[role="button"], *[ng-click], *[data-ng-click],[href]');
        for (var i = 0; i < elems.length; i++) {
            if(elems[i].tagName.toLowerCase() === 'input'){
                text = elems[i].value;
            }
            else {
                text = elems[i].innerText;
            }
            if (text.trim() === locator){
                full.push(elems[i]);
            }
            else if (text.trim().toLowerCase() === locator.toLowerCase()){
                partial.push(elems[i]);
            }
        }
        candidates = full.concat(partial);
        return candidates;
    }
    return(web_elements('""" + locator.replace("\'", "\\'") + """'));"""
    return execute_javascript(js)


def get_recursive_walk() -> str:
    return """var recursiveWalk = function(node, func) {
    var done = func(node);
    if(done) {
        return true;
    }
    if ('shadowRoot' in node && node.shadowRoot) {
        var done = recursiveWalk(node.shadowRoot, func);
        if (done) {
            return true;
        }
    }
    node = node.firstChild;

    while (node) {
        var done = recursiveWalk(node, func);
        if (done) {
            return true;
        }
        node = node.nextSibling;
    }

    }"""


def get_text_elements_from_shadow_dom(locator: str, partial: bool) -> list[WebElement]:
    js = get_recursive_walk() + """
    function find_text_from_shadow_dom(text, partial){
        var results = [];
        var unsupported_tags = ["script", "#document-fragment"]
        var elem = recursiveWalk(document.body, function(node) {
        //if (node.innerText == text) {
        // handle non-breaking spaces, they are not considered the same as normal space
        // when querying textContent
        if (node.textContent.replace(/\u00a0/g, ' ').includes(text) && !unsupported_tags.includes(node.nodeName.toLowerCase())) {
            nodetext = [].reduce.call(node.childNodes, function(a, b) { return a + (b.nodeType === 3 ? b.textContent.trim() : ''); }, '');
            // handle non-breaking spaces
            nodetext = nodetext.replace(/\u00A0/g, ' ')
            if (nodetext == text) {
                results.push(node);
            }
            else if (partial && nodetext.includes(text)) {
                 results.push(node)
            }
        }
        else if (node.placeholder === text || node.value === text) {
                results.push(node)
        }
    });

        return results;
    }
    return(find_text_from_shadow_dom(arguments[0], arguments[1]))"""
    return execute_javascript(js, locator, partial)


def get_clickable_from_shadow_dom(locator: str, partial: bool) -> list[WebElement]:
    js = get_recursive_walk() + """
    function find_clickable_from_shadow_dom(text, partial){
        var results = [];
        var full = [];
        var parts = [];
        var clickable_types = ["button", "reset", "submit"]
        var elem = recursiveWalk(document.body, function(node) {
            try {
                if ((node.getAttribute('onclick')!=null) ||
                   (node.getAttribute('href')!=null) ||
                   (node.getAttribute('role')=='button') ||
                   (clickable_types.includes(node.getAttribute('type')))) {
                    if (node.tagName.toLowerCase() == "input" && node.type("radio")) {
                        nodetext = node.value;
                    }
                    else {
                        nodetext = node.innerText;
                    }
                    if(nodetext.trim() === text) {
                        full.push(node);
                    }
                    else if (partial && nodetext.trim().includes(text)) {
                        parts.push(node)
                    }
                }
            } catch(ex) {}
        });
        results = full.concat(parts);
        return results;
    }
    return(find_clickable_from_shadow_dom(arguments[0], arguments[1]))"""
    return execute_javascript(js, locator, partial)


def get_all_frames_from_shadow_dom() -> list[WebElement]:
    js = get_recursive_walk() + """
    function find_all_frames_from_shadow_dom(){
        var results = [];
        var elem = recursiveWalk(document.body, function(node) {
            if (node.tagName == "IFRAME" || node.tagName == "FRAME") {
                    results.push(node);
            }

        });
        return results;
    }

    return(find_all_frames_from_shadow_dom(arguments[0]))"""
    return execute_javascript(js)


def get_all_input_elements_from_shadow_dom() -> list[WebElement]:
    js = get_recursive_walk() + """
    function find_all_input_elements_from_shadow_dom(){
        var results = [];
        var elem = recursiveWalk(document.body, function(node) {
            if (node.tagName == "INPUT" || node.tagName == "TEXTAREA") {
                    results.push(node);
            }

        });
        return results;
    }

    return(find_all_input_elements_from_shadow_dom(arguments[0]))"""
    return execute_javascript(js)


def get_all_dropdown_elements_from_shadow_dom() -> list[WebElement]:
    js = get_recursive_walk() + """
    function find_all_select_elements_from_shadow_dom(){
        var results = [];
        var elem = recursiveWalk(document.body, function(node) {
            if (node.tagName == "SELECT") {
                    results.push(node);
            }

        });
        return results;
    }

    return(find_all_select_elements_from_shadow_dom(arguments[0]))"""
    return execute_javascript(js)


def get_item_elements_from_shadow_dom(tag: str) -> list[WebElement]:
    js = get_recursive_walk() + """
    function find_item_elements_from_shadow_dom(tag){
        var results = [];
        var supported_tags = tag === null ? ["A", "SPAN", "IMG", "LI", "H1", "H2", "H3", "H4", "H5", "H6", "DIV", "SVG", "P", "BUTTON", "INPUT", "TEXTAREA"] : [tag.toUpperCase()];
        var elem = recursiveWalk(document.body, function(node) {
            if (supported_tags.includes(node.tagName)) {
                    results.push(node);
            }

        });
        return results;
    }

    return(find_item_elements_from_shadow_dom(arguments[0], arguments[1]))"""
    return execute_javascript(js, tag)
