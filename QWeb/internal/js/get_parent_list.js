// get_parent_list.js
// Gets parent list for a web element, with special handling for list tags

function getParentList(locator, css) {
    var list_tags = ["ul", "ol", "dl", "UL", "OL", "DL"];
    if (list_tags.includes(css)) {
        if ((locator.parentNode.tagName === "UL" || locator.parentNode.tagName === "OL" || locator.parentNode.tagName === "DL") && locator.parentNode.parentNode.tagName === css.toUpperCase()) {
            return locator.parentNode.parentNode;
        } else if (locator.parentNode.parentNode.parentNode.tagName === css.toUpperCase()) {
            return locator.parentNode.parentNode.parentNode;
        }
    } else {
        return locator.parentNode.parentNode;
    }
    return [];
}

// Entrypoint for Selenium execute_script
return getParentList(arguments[0], arguments[1]);
