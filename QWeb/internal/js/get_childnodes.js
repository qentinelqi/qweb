// get_childnodes.js
// Finds matching child nodes for a given locator element, with optional upward traversal

function getChildNodes(locator, selector, level, traverse) {
    if (locator.querySelectorAll(selector).length > 0) {
        return locator.querySelectorAll(selector);
    } else if (traverse) {
        for (var i = 0; i < level; i++) {
            locator = locator.parentNode;
            if (locator.querySelectorAll(selector).length > 0)
                return locator.querySelectorAll(selector);
        }
    }
    return [];
}

// Entrypoint for Selenium execute_script
return getChildNodes(arguments[0], arguments[1], arguments[2], arguments[3]);
