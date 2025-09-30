// get_by_label.js
// Finds elements based on their label, supporting for-attribute and DOM traversal

function traverseLabel(locator, selector, level) {
    if (locator.querySelectorAll(selector).length > 0) {
        return locator.querySelectorAll(selector);
    } else {
        for (var i = 0; i < level; i++) {
            locator = locator.parentNode;
            if (locator.querySelectorAll(selector).length > 0)
                return locator.querySelectorAll(selector);
        }
    }
    return [];
}

function getByFor(needle, haystack) {
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

function getByLabel(locator, selector, level, partial) {
    var elems = document.querySelectorAll('label');
    var haystack = document.querySelectorAll(selector);
    var matches = {};
    var full_matches = [];
    var part_with_for = [];
    var part_matches = [];
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].hasAttribute('for') && elems[i].innerText.trim() === locator) {
            var needle = elems[i].getAttribute('for');
            var target = getByFor(needle, haystack);
            if (target) {
                full_matches.push(target);
                continue;
            }
        } else if (elems[i].innerText.trim() === locator) {
            var target = traverseLabel(elems[i], selector, level)[0];
            if (target) {
                full_matches.push(target);
                continue;
            }
        }
        if (partial === true) {
            if (elems[i].hasAttribute('for') && elems[i].innerText.trim().includes(locator)) {
                var needle = elems[i].getAttribute('for');
                var target = getByFor(needle, haystack);
                if (target) {
                    part_with_for.push(target);
                    continue;
                }
            } else if (elems[i].innerText.trim().includes(locator)) {
                var target = traverseLabel(elems[i], selector, level)[0];
                if (target) {
                    part_matches.push(target);
                }
            }
        }
    }
    matches = { full: full_matches.concat(part_with_for), partial: part_matches };
    return matches;
}

// Entrypoint for Selenium execute_script
return getByLabel(arguments[0], arguments[1], arguments[2], arguments[3]);
